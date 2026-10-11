import codecs
import random
import os
import shlex
import shutil
import subprocess
import sys
from itertools import permutations
from pathlib import Path

import pytest

from fastapi.testclient import TestClient

from T32026.GA1.app import app
from T32026.GA1.termlog import decode_termlog


def encode(value, order):
    for step in order:
        if step == "hex":
            value = value.encode("utf-8").hex()
        elif step == "reverse":
            value = value[::-1]
        else:
            value = codecs.encode(value, "rot_13")
    return value


def test_every_transform_order_across_generated_students():
    rng = random.Random(13)
    for student in range(250):
        plaintext = f"T3-code-{student}-" + ''.join(rng.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=24))
        for order in permutations(("rot13", "hex", "reverse")):
            result = decode_termlog(encode(plaintext, order))
            assert plaintext in [c["plaintext"] for c in result["candidates"]]
            for candidate in result["candidates"]:
                for inverse in candidate["decode_orders"]:
                    assert encode(candidate["plaintext"], reversed(inverse)) == encode(plaintext, order)


def test_ambiguity_is_not_reported_as_a_definite_answer():
    # Both ab and ba are possible because reversal and ROT13 commute.
    result = decode_termlog("6162")
    assert result["status"] == "ambiguous"
    assert result["answer"] is None


def test_unicode_multiline_preserved_and_no_execution():
    plaintext = "Hello café\nworld\t$(touch never-execute)"
    result = decode_termlog(encode(plaintext, ("rot13", "reverse", "hex")))
    assert plaintext in [c["plaintext"] for c in result["candidates"]]
    for candidate in result["candidates"]:
        assert "touch never-execute" not in ' '.join(candidate["shell_pipelines"])
        assert "sys.stdin.buffer.read()" in ' '.join(candidate["shell_pipelines"])


def test_api_validation_no_onboarding_and_tenant_alias():
    with TestClient(app) as client:
        for route in ("/q13/decode", "/student@example.com/q13/decode", "/other@example.com/q13/decode"):
            response = client.post(route, json={"ciphertext": "6162"})
            assert response.status_code == 200
            assert response.headers["cache-control"] == "no-store"
            assert response.json()["answer"] is None
        for body in ({}, [], {"ciphertext": 123}, {"ciphertext": ""}, {"ciphertext": "é"}, {"ciphertext": "a" * 16385}):
            assert client.post("/q13/decode", json=body).status_code == 400
        assert client.post("/q13/decode", content="{", headers={"Content-Type": "application/json"}).status_code == 400
        assert client.post("/q13/decode", json={"ciphertext": "!not hex!"}).status_code == 422
        assert client.post("/q13/decode", content="x" * 32769).status_code == 413


def test_limits_whitespace_and_invalid_hex():
    for value in (None, 12, "", " " * 16385, "é6162", "\x006162", "616", "ff", "00", "0g"):
        if not isinstance(value, str) or not value.strip() or not value.isascii():
            with pytest.raises(ValueError):
                decode_termlog(value)
        else:
            assert not decode_termlog(value)["candidates"]
    assert decode_termlog(" \r\n6162\t ") == decode_termlog("6162")
    assert decode_termlog("41" * 8192)["candidates"]
    with pytest.raises(ValueError):
        decode_termlog("41" * 8192 + " ")


def test_generated_shell_pipelines_match_decoder(tmp_path):
    # Execute only our constant command templates against fixture files. Never
    # interpolate plaintext or ciphertext into executable shell source.
    git_bash = Path("C:/Program Files/Git/bin/bash.exe")
    bash = str(git_bash) if os.name == "nt" and git_bash.exists() else shutil.which("bash")
    if not bash:
        pytest.skip("Bash unavailable")
    # Map python3 to the running test interpreter (Windows aliases can be stubs).
    prefix = "python3() { " + shlex.quote(Path(sys.executable).as_posix()) + ' "$@"; }; '
    probe = subprocess.run([bash, "-c", "command -v xxd && command -v tr"], capture_output=True, timeout=10)
    if probe.returncode:
        pytest.skip("xxd/tr unavailable")
    plaintext = "Hello café\r\nworld\t$(touch SHOULD_NOT_EXIST)\n"
    for order in permutations(("rot13", "hex", "reverse")):
        source = encode(plaintext, order)
        (tmp_path / "cipher.txt").write_bytes((" \n" + source + "\r\n ").encode("ascii"))
        for candidate in decode_termlog(source)["candidates"]:
            for pipeline in candidate["shell_pipelines"]:
                result = subprocess.run([bash, "-c", prefix + "set -o pipefail; " + pipeline], cwd=tmp_path, capture_output=True, timeout=10)
                assert result.returncode == 0, result.stderr
                assert result.stdout.decode("utf-8") == candidate["plaintext"]
    assert not (tmp_path / "SHOULD_NOT_EXIST").exists()


def test_mounted_hub_q13_route_and_student_middleware():
    from hf_space.app import app as hub
    with TestClient(hub) as client:
        expected = client.post("/ga1/q13/decode", json={"ciphertext": "6162"})
        assert expected.status_code == 200
        for email in ("student", "other"):
            result = client.post(f"/ga1/{email}%40example.com/q13/decode", json={"ciphertext": "6162"})
            assert result.status_code == 200
            assert result.json() == expected.json()
