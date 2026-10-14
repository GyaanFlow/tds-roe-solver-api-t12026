"""Answer computations for the T3-2026 GA1 questions that are graded by ``/backendVerify``
but whose answer is derived from the student's own data:

* ``q-cosine-similarity-server``  - dataset is generated from the email seed alone.
* ``q-git-forensics-token-server`` - parsed from the student's signed git fast-import stream.
* ``q-http-headers-server``       - ``X-Exam-Code`` header of the student's signed resource.

Each function only reproduces what the question asks the student to compute; the
official ``/backendVerify`` remains the authority on whether the answer is correct.
"""
from __future__ import annotations

import base64
import math
import re
from typing import Any
from urllib.parse import unquote

from T22026.shared.seedrandom_arc4 import SeedRandom

# ------------------------------------------------------------------ cosine similarity

COSINE_QUESTION_ID = "q-cosine-similarity-server"
_COSINE_SEED = "tds-2026-05-ga3-cosine-sim-client-v1"
_DIM, _DOCS, _QUERIES, _TOP = 64, 250, 10, 5
_TOPIC_WORDS: dict[str, list[str]] = {
    "ML": ["neural", "gradient", "backprop", "loss", "epoch", "batch", "model", "train", "feature", "weight", "activation", "layer", "dropout", "learning", "inference", "embedding", "transformer", "attention"],
    "DATA": ["query", "database", "index", "schema", "table", "row", "column", "join", "aggregate", "filter", "pipeline", "etl", "warehouse", "stream", "batch", "partition", "shard", "replica"],
    "WEB": ["http", "request", "response", "cache", "cookie", "session", "token", "api", "endpoint", "rest", "graphql", "websocket", "latency", "throughput", "bandwidth", "proxy", "cdn", "tls"],
    "MATH": ["vector", "matrix", "eigenvalue", "integral", "derivative", "probability", "distribution", "variance", "covariance", "correlation", "regression", "hypothesis", "bayes", "entropy", "gradient", "manifold"],
    "CLOUD": ["container", "kubernetes", "docker", "pod", "service", "deployment", "scaling", "ingress", "node", "cluster", "autoscale", "loadbalancer", "microservice", "serverless", "function", "bucket", "volume"],
}


def cosine_dataset(email: str, version: str = "") -> tuple[list[tuple[str, list[float]]], list[tuple[str, list[float]]]]:
    """Regenerate the student's documents/queries exactly as the exam page does."""
    rng = SeedRandom(f"{_COSINE_SEED}#{str(email or '').strip().lower()}#{version}")
    topics = list(_TOPIC_WORDS)

    def gaussian() -> float:
        u = v = 0.0
        while u == 0:
            u = rng()
        while v == 0:
            v = rng()
        return math.sqrt(-2 * math.log(u)) * math.cos(2 * math.pi * v)

    def unit_gaussian(n: int) -> list[float]:
        values = [gaussian() for _ in range(n)]
        norm = math.sqrt(sum(x * x for x in values))
        return [x / norm for x in values]

    def mix(base: list[float]) -> list[float]:
        noise = unit_gaussian(_DIM)
        mixed = [b * 0.85 + n * 0.15 for b, n in zip(base, noise)]
        norm = math.sqrt(sum(x * x for x in mixed))
        return [x / norm for x in mixed]

    centers = {topic: unit_gaussian(_DIM) for topic in topics}
    documents, queries = [], []
    for index in range(_DOCS):
        topic = topics[index % len(topics)]
        embedding = mix(centers[topic])
        for _ in range(4):  # title words consume RNG draws; keep the stream aligned
            rng()
        documents.append((f"D{index + 1:06d}", embedding))
    for index in range(_QUERIES):
        topic = topics[index % len(topics)]
        embedding = mix(centers[topic])
        for _ in range(3):
            rng()
        queries.append((f"Q{index + 1:03d}", embedding))
    return documents, queries


def cosine_answer(email: str, version: str = "") -> dict[str, list[str]]:
    documents, queries = cosine_dataset(email, version)
    answer: dict[str, list[str]] = {}
    for query_id, query in queries:
        scored = [(sum(a * b for a, b in zip(query, vector)), doc_id) for doc_id, vector in documents]
        # Highest similarity first; equal similarity -> smaller doc_id first.
        scored.sort(key=lambda item: (-item[0], item[1]))
        answer[query_id] = [doc_id for _, doc_id in scored[:_TOP]]
    return answer


# ----------------------------------------------------------------- headers code

HEADERS_QUESTION_ID = "q-http-headers-server"


def headers_code(headers: Any) -> str:
    code = (headers.get("x-exam-code") or "").strip() if hasattr(headers, "get") else ""
    if not code:
        raise ValueError("NO_X_EXAM_CODE_HEADER")
    return code


# ---------------------------------------------------------------- git forensics

GIT_QUESTION_ID = "q-git-forensics-token-server"
_TOKEN_RE = re.compile(r"stg_[A-Za-z0-9_\-]+")
_DATA_URI_RE = re.compile(r'download="history\.fastimport"[^>]*href="(data:[^"]+)"|href="(data:application/octet-stream;base64,[^"]+)"')
MAX_STREAM_BYTES = 12 * 1024 * 1024


def extract_fastimport(page: bytes | str) -> bytes:
    """The viewer page embeds the stream as a base64 data URI; fall back to a raw stream."""
    text = page.decode("utf-8", "replace") if isinstance(page, bytes) else page
    match = _DATA_URI_RE.search(text)
    if not match:
        return page if isinstance(page, bytes) else page.encode("utf-8")
    uri = match.group(1) or match.group(2)
    head, _, payload = uri.partition(",")
    if ";base64" in head:
        return base64.b64decode(re.sub(r"\s+", "", payload) + "===")
    return unquote(payload).encode("latin-1", "replace")


class _Commit:
    __slots__ = ("parents", "msg", "ops", "mark")

    def __init__(self):
        self.parents: list[_Commit] = []
        self.msg: bytes | None = None
        self.ops: list[tuple[str, str, bytes | None]] = []
        self.mark: str | None = None


def _unquote_path(path: str) -> str:
    if len(path) >= 2 and path.startswith('"') and path.endswith('"'):
        return re.sub(r"\\(.)", r"\1", path[1:-1])
    return path


def parse_fastimport(buf: bytes) -> tuple[list[_Commit], int]:
    """Byte-exact fast-import parser: ``data N`` counts bytes, not characters."""
    pos = 0
    n = len(buf)

    def read_line() -> str | None:
        nonlocal pos
        if pos >= n:
            return None
        end = buf.find(b"\n", pos)
        if end < 0:
            end = n
        line = buf[pos:end].decode("utf-8", "replace")
        pos = end + 1
        return line[:-1] if line.endswith("\r") else line

    def read_n(count: int) -> bytes:
        nonlocal pos
        chunk = buf[pos:pos + count]
        pos += count
        if pos < n and buf[pos] == 10:
            pos += 1
        return chunk

    blobs: dict[str, bytes] = {}
    commits: list[_Commit] = []
    by_mark: dict[str, _Commit] = {}
    current: _Commit | None = None
    while True:
        line = read_line()
        if line is None:
            break
        if line == "blob":
            mark = None
            while True:
                inner = read_line()
                if inner is None:
                    break
                if inner.startswith("mark "):
                    mark = inner[5:].strip()
                    continue
                m = re.fullmatch(r"data (\d+)", inner)
                if m:
                    data = read_n(int(m[1]))
                    if mark:
                        blobs[mark] = data
                    break
                if inner == "":
                    break
            continue
        if line.startswith("commit "):
            current = _Commit()
            commits.append(current)
            continue
        if current is None:
            continue
        if line.startswith("mark "):
            current.mark = line[5:].strip()
            by_mark[current.mark] = current
            continue
        if line.startswith(("from ", "merge ")):
            ref = line.split(" ", 1)[1].strip()
            if ref in by_mark:
                current.parents.append(by_mark[ref])
            continue
        if line.startswith(("author ", "committer ")) or line == "":
            continue
        m = re.fullmatch(r"data (\d+)", line)
        if m:
            data = read_n(int(m[1]))
            if current.msg is None:
                current.msg = data
            continue
        if line.startswith("M "):
            m = re.match(r"^(\S+)\s+(\S+)\s+([\s\S]*)$", line[2:])
            if m:
                ref, path = m[2], _unquote_path(m[3])
                if ref == "inline":
                    header = read_line()
                    dm = re.fullmatch(r"data (\d+)", header or "")
                    current.ops.append(("M", path, read_n(int(dm[1])) if dm else b""))
                else:
                    current.ops.append(("M", path, blobs.get(ref)))
            continue
        if line.startswith("D "):
            current.ops.append(("D", _unquote_path(line[2:].strip()), None))
    return commits, len(blobs)


def find_git_token(buf: bytes) -> dict[str, Any]:
    """Replay history oldest-first and return the first commit whose tree contains the token."""
    commits, _ = parse_fastimport(buf)
    seen: set[int] = set()
    order: list[_Commit] = []

    def visit(commit: _Commit):
        stack = [(commit, False)]
        while stack:
            node, expanded = stack.pop()
            if expanded:
                order.append(node)
                continue
            if id(node) in seen:
                continue
            seen.add(id(node))
            stack.append((node, True))
            for parent in reversed(node.parents):
                stack.append((parent, False))

    for commit in commits:
        visit(commit)
    state: dict[str, bytes] = {}
    for commit in order:
        for kind, path, content in commit.ops:
            if kind == "D":
                state.pop(path, None)
            elif content is not None:
                state[path] = content
        for content in state.values():
            match = _TOKEN_RE.search(content.decode("utf-8", "replace"))
            if match:
                subject = (commit.msg or b"").decode("utf-8", "replace").split("\n")[0].strip()
                return {"token": match[0], "commit_subject": subject, "commits": len(commits)}
    raise ValueError("NO_STG_TOKEN_IN_HISTORY")
