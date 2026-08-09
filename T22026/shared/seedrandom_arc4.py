from __future__ import annotations

"""
T22026/shared/seedrandom_arc4.py — shared ARC4-based seedrandom port.

The npm `seedrandom` package's DEFAULT export (David Bau's ARC4-based
Math.seedrandom, NOT Alea). Every GA6/GA7 exam question that assigns
per-student values calls `seedrandom(stringSeed)` directly -- this is a
faithful line-for-line port of node_modules/seedrandom/seedrandom.js's
no-options, string-seed calling path.

Originally built and verified for GA6 Q7 (see T22026/GA6/solvers.py's
docstring for the full story of how the Alea-vs-ARC4 mistake was caught).
Verified bit-for-bit against the real npm package across 10+ emails/edge
cases (empty string, very long string, spaces, mixed case) -- 0 mismatches.
Re-verified again for GA7's four seeded questions (action-firewall,
terraform-plan-guard, llm-output-sanitizer, osint-corroboration) against
`node -e "require('seedrandom')(...)"` output before trusting this for them.

Extracted here so GA6 and GA7 share one algorithm instead of two copies that
could silently drift.
"""

from typing import List

_ARC4_WIDTH = 256
_ARC4_CHUNKS = 6
_ARC4_DIGITS = 52
_ARC4_MASK = _ARC4_WIDTH - 1
_ARC4_STARTDENOM = float(_ARC4_WIDTH ** _ARC4_CHUNKS)
_ARC4_SIGNIFICANCE = float(2 ** _ARC4_DIGITS)
_ARC4_OVERFLOW = _ARC4_SIGNIFICANCE * 2


def _to_int32(x: float) -> int:
    xi = int(x) & 0xFFFFFFFF
    return xi - 0x100000000 if xi >= 0x80000000 else xi


def _mixkey(seed: str, key: List[int]) -> None:
    """seedrandom.js's mixkey(): `key[mask&j] = mask & ((smear ^= key[mask&j]*19)
    + charCodeAt(j))`. In JS, reading an unset array slot gives `undefined`,
    and `undefined * 19` is NaN -- which coerces to 0 under `^` (ToInt32). For
    any seed under 256 chars (every realistic email/questionId string), each
    index is touched only once, so `smear` provably never becomes anything
    but 0 the whole way through. Ported as the literal loop anyway so it
    stays correct even if that assumption is ever violated."""
    smear = 0
    for j, ch in enumerate(seed):
        idx = _ARC4_MASK & j
        prev = key[idx] if idx < len(key) else None
        term = float("nan") if prev is None else float(prev * 19)
        term_i32 = 0 if term != term else _to_int32(term)  # NaN check
        smear = _to_int32(smear) ^ term_i32
        val = _ARC4_MASK & (smear + ord(ch))
        if idx < len(key):
            key[idx] = val
        else:
            key.append(val)


class _ARC4:
    def __init__(self, key: List[int]) -> None:
        keylen = len(key)
        if keylen == 0:
            key = [0]
            keylen = 1
        s = list(range(_ARC4_WIDTH))
        j = 0
        for i in range(_ARC4_WIDTH):
            t = s[i]
            j = _ARC4_MASK & (j + key[i % keylen] + t)
            s[i] = s[j]
            s[j] = t
        self.S = s
        self.i = 0
        self.j = 0
        # RC4-drop[256]: the real source defines g() and immediately calls it
        # with count=width (256), discarding the result, right after key
        # scheduling -- `(me.g=function(count){...})(width)`. Skipping this
        # silently desyncs every subsequent output from the real generator.
        self.g(_ARC4_WIDTH)

    def g(self, count: int) -> int:
        s = self.S
        i, j = self.i, self.j
        r = 0
        for _ in range(count):
            i = _ARC4_MASK & (i + 1)
            t = s[i]
            j = _ARC4_MASK & (j + t)
            s[i], s[j] = s[j], t
            r = r * _ARC4_WIDTH + s[_ARC4_MASK & (s[i] + s[j])]
        self.i, self.j = i, j
        return r


class SeedRandom:
    """Callable PRNG matching `rng()` -> float in [0, 1), i.e. JS `seedrandom(seed)()`."""

    def __init__(self, seed: str) -> None:
        key: List[int] = []
        _mixkey(seed, key)
        self._arc4 = _ARC4(key)

    def next(self) -> float:
        arc4 = self._arc4
        n = float(arc4.g(_ARC4_CHUNKS))
        d = _ARC4_STARTDENOM
        x = 0
        while n < _ARC4_SIGNIFICANCE:
            n = (n + x) * _ARC4_WIDTH
            d *= _ARC4_WIDTH
            x = arc4.g(1)
        while n >= _ARC4_OVERFLOW:
            n /= 2
            d /= 2
            x >>= 1
        return (n + x) / d

    def __call__(self) -> float:
        return self.next()
