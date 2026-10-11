"""Stateless Q13 decoding assistance; never execute input or create recordings."""
from __future__ import annotations

import codecs
import re
from itertools import permutations

_ROT13_SHELL = "LC_ALL=C tr 'A-Za-z' 'N-ZA-Mn-za-m'"
_COMMANDS = {"rot13": _ROT13_SHELL, "hex": "xxd -r -p", "reverse": "python3 -c 'import sys; sys.stdout.buffer.write(sys.stdin.buffer.read().decode(\"utf-8\")[::-1].encode(\"utf-8\"))'"}
_INPUT_SHELL = "python3 -c 'import sys; sys.stdout.buffer.write(sys.stdin.buffer.read().strip())' < cipher.txt"


def decode_termlog(ciphertext: str) -> dict:
    # The challenge is a single encoded string. Permit surrounding whitespace,
    # but do not silently delete interior characters or guess nested JSON fields.
    if not isinstance(ciphertext, str) or len(ciphertext) > 16384 or not ciphertext.isascii():
        raise ValueError("CIPHERTEXT_REQUIRED_ASCII_MAX_16384")
    source = ciphertext.strip()
    if not source:
        raise ValueError("CIPHERTEXT_REQUIRED_ASCII_MAX_16384")
    candidates: dict[str, dict] = {}
    for order in permutations(("rot13", "hex", "reverse")):
        value = source
        try:
            for step in order:
                if step == "rot13":
                    value = codecs.decode(value, "rot_13")
                elif step == "reverse":
                    value = value[::-1]
                else:
                    if len(value) % 2 or not re.fullmatch(r"[0-9a-fA-F]+", value):
                        raise ValueError("Not hex")
                    value = bytes.fromhex(value).decode("utf-8", errors="strict")
        except (ValueError, UnicodeError):
            continue
        # Readability is a filter, not proof of correctness. Keep all distinct
        # readable outputs, including both orientations when they are valid.
        if not value or not all(c.isprintable() or c in "\n\r\t" for c in value):
            continue
        record = candidates.setdefault(value, {"plaintext": value, "decode_orders": [], "shell_pipelines": []})
        record["decode_orders"].append(list(order))
        # Input stays in a file; never interpolate ciphertext into shell syntax.
        record["shell_pipelines"].append(_INPUT_SHELL + " | " + " | ".join(_COMMANDS[s] for s in order))
    results = list(candidates.values())
    status = "unique_readable_candidate" if len(results) == 1 else "ambiguous" if results else "no_readable_candidate"
    return {
        "status": status,
        "answer": results[0]["plaintext"] if len(results) == 1 else None,
        "candidates": results,
        "submission_type": "public_url_of_signed_termlog_archive",
        "instructions": "Fetch and decode the current challenge using shell commands inside your own termlog recording. Submit the archive URL, not this API URL. Readable candidates are not grader verification.",
    }
