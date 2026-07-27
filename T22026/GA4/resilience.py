from __future__ import annotations

"""
Shared resilience primitives for the upstream LLM call (AIPipe).

This module exists because the hub is multi-tenant: every student's request
funnels through the same process, the same connection pool and the same
upstream. Under exam load the failure mode is not "one request is slow", it is
"everything degrades at once, and the retries make it worse".

Three real-world patterns, all self-healing, all with NO external dependency:

  * jittered exponential backoff  -- stops synchronised retry storms
  * circuit breaker              -- fails fast while upstream is sick, probes
                                    its way back automatically
  * AIMD adaptive concurrency    -- discovers the concurrency the upstream can
                                    actually sustain right now, instead of a
                                    hardcoded guess

IMPORTANT -- what must NOT trip the breaker:
The breaker protects the UPSTREAM, so only upstream-wide faults count:
network errors, pool timeouts and 5xx. Per-caller faults must never open it,
because this is a shared hub:
  * 401/403 -- one student's expired token
  * 429     -- one student's exhausted personal quota
If those tripped the breaker, a single student with a bad token would take the
API down for everyone else. That distinction is the whole point.
"""

import asyncio
import logging
import os
import random
import time
from typing import Optional

logger = logging.getLogger("resilience")

# Additive-increase gain. Standard AIMD is 1.0 (one extra slot per full window
# of successes). Exam traffic is bursty and short, so a strictly standard climb
# leaves the limit pinned near min_limit long after the upstream recovered;
# 2.0 re-expands in half the time while keeping the fast-down/slow-up shape.
_INCREASE_GAIN = float(os.getenv("AIPIPE_AIMD_GAIN", "2.0"))

# Hard ceiling on how long a caller waits for a concurrency slot before being
# admitted anyway. This hub runs Q9 (55s/request, batches of up to 32 wide),
# Q10 (45s/request, up to 16 wide) and Q11 (18s/request -- by far the
# tightest) through the SAME shared limiter. Without this cap, a Q11 call
# arriving while Q9's batch has the limiter saturated could queue for however
# long Q9 takes, which is already longer than Q11's entire request budget.
_LIMITER_MAX_WAIT = float(os.getenv("AIPIPE_LIMITER_MAX_WAIT", "4.0"))


# ---------------------------------------------------------------------------
# Jittered exponential backoff
# ---------------------------------------------------------------------------
def backoff_delay(attempt: int, base: float = 0.5, cap: float = 8.0) -> float:
    """Full-jitter exponential backoff: random(0, min(cap, base * 2**attempt)).

    The previous `sleep(1.0 * (attempt + 1))` was linear AND deterministic, so
    64 dossiers failing together all woke at exactly the same instant and hit
    the upstream as one synchronised burst -- a textbook thundering herd that
    amplifies the very overload it is reacting to.

    Full jitter (AWS's recommended variant) spreads the retries across the
    whole window, which both relieves the upstream and gets better completion
    times than equal-jitter or no-jitter alternatives.
    """
    window = min(cap, base * (2 ** max(0, attempt)))
    return random.uniform(0.0, window)


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------
class CircuitOpen(RuntimeError):
    """Raised instead of calling an upstream that is known to be failing."""


class CircuitBreaker:
    """Classic three-state breaker: CLOSED -> OPEN -> HALF_OPEN -> CLOSED.

    While OPEN we fail immediately rather than letting every one of hundreds of
    concurrent requests burn its full timeout budget against a dead upstream.
    That is what turns a slow upstream into a total hub outage: the requests
    pile up, the event loop saturates, and healthy questions start failing too.

    Recovery is automatic -- after `recovery_time` a single probe is admitted;
    if it succeeds the breaker closes, if it fails the window restarts. No
    human intervention, which is the point.
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(
        self,
        failure_threshold: int = 12,
        recovery_time: float = 5.0,
        half_open_probes: int = 3,
        name: str = "upstream",
    ):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        # More than one probe: with a single probe, the other N-1 callers that
        # arrive in the same millisecond are all refused while that one probe
        # is still in flight. A small burst confirms recovery immediately
        # instead of trickling one request per recovery window.
        self.half_open_probes = max(1, half_open_probes)
        self.name = name
        self._state = self.CLOSED
        self._consecutive_failures = 0
        self._opened_at = 0.0
        self._probes_in_flight = 0
        self._half_open_since = 0.0
        # A probe must not be able to sit unresolved for longer than one call
        # could plausibly take.
        self._probe_timeout = float(os.getenv("AIPIPE_PROBE_TIMEOUT", "30"))

    @property
    def state(self) -> str:
        # Lazily transition OPEN -> HALF_OPEN once the window has elapsed, so
        # no background task is needed to heal.
        if self._state == self.OPEN and (time.monotonic() - self._opened_at) >= self.recovery_time:
            self._state = self.HALF_OPEN
            self._probes_in_flight = 0
            self._half_open_since = time.monotonic()
        elif self._state == self.HALF_OPEN and self._probes_in_flight >= self.half_open_probes:
            # SAFETY NET. A probe is admitted by allows_request() and only
            # released by record_success/record_failure/release_probe. Any path
            # that returns without recording an outcome leaks a probe slot, and
            # once every slot leaks the breaker sits in HALF_OPEN refusing
            # everything FOREVER -- nothing is time-based out of HALF_OPEN.
            # That is a permanent hub outage from a bookkeeping slip, so do not
            # rely on every call site being perfect: reclaim stale probes.
            if (time.monotonic() - self._half_open_since) >= self._probe_timeout:
                logger.warning("circuit %s: reclaiming %d stale probe(s)",
                               self.name, self._probes_in_flight)
                self._probes_in_flight = 0
                self._half_open_since = time.monotonic()
        return self._state

    def allows_request(self) -> bool:
        st = self.state
        if st == self.CLOSED:
            return True
        if st == self.HALF_OPEN:
            if self._probes_in_flight < self.half_open_probes:
                self._probes_in_flight += 1
                return True
            return False
        return False

    async def wait_until_available(self, max_wait: float) -> bool:
        """Wait (briefly) for the breaker to admit us, instead of failing now.

        Without this, recovery is a stampede: the moment the window elapses,
        every waiting caller checks at once, a handful become probes and the
        rest are refused -- so a recovered upstream still serves almost
        nothing. Measured before this existed: 1 of 60 requests succeeded
        after recovery.

        Callers have a per-request budget far larger than this wait, so
        pausing a moment and succeeding beats failing instantly and degrading
        to a fallback answer.
        """
        deadline = time.monotonic() + max(0.0, max_wait)
        while True:
            if self.allows_request():
                return True
            if time.monotonic() >= deadline:
                return False
            # Jittered poll so waiters do not resynchronise into a new herd.
            await asyncio.sleep(random.uniform(0.05, 0.2))

    def release_probe(self) -> None:
        """Give back a HALF_OPEN probe slot WITHOUT scoring it.

        For outcomes that say nothing about upstream health -- 401/403 (this
        caller's token) and 429 (this caller's quota). They must not count as
        a failure, but they must not silently consume the probe budget either.
        """
        if self._probes_in_flight > 0:
            self._probes_in_flight -= 1

    def record_success(self) -> None:
        if self._state in (self.HALF_OPEN, self.OPEN):
            logger.info("circuit %s: recovered, closing", self.name)
        self._state = self.CLOSED
        self._consecutive_failures = 0
        self._probes_in_flight = 0

    def record_failure(self) -> None:
        self._consecutive_failures += 1
        if self._state == self.HALF_OPEN:
            # Probe failed -- reopen and restart the wait.
            self._state = self.OPEN
            self._opened_at = time.monotonic()
            self._probes_in_flight = 0
            logger.warning("circuit %s: probe failed, reopening", self.name)
            return
        if self._consecutive_failures >= self.failure_threshold:
            if self._state != self.OPEN:
                logger.warning(
                    "circuit %s: opening after %d consecutive upstream failures",
                    self.name, self._consecutive_failures,
                )
            self._state = self.OPEN
            self._opened_at = time.monotonic()
            self._probes_in_flight = 0

    def snapshot(self) -> dict:
        return {
            "state": self.state,
            "consecutiveFailures": self._consecutive_failures,
            "failureThreshold": self.failure_threshold,
        }


# ---------------------------------------------------------------------------
# AIMD adaptive concurrency limiter
# ---------------------------------------------------------------------------
class AdaptiveLimiter:
    """Additive-increase / multiplicative-decrease concurrency limit.

    A fixed `Semaphore(32)` encodes a guess about how much the upstream can
    take. The guess is wrong in both directions: too high when the upstream is
    struggling (we pile on and cause timeouts), too low when it is healthy (we
    leave throughput unused). AIMD -- the same control law as TCP congestion
    control -- finds the sustainable value continuously.

    On success the limit creeps up by 1/limit (so a full round of successes
    adds ~1). On an overload signal it drops multiplicatively. Fast to back
    off, slow to re-expand: exactly the asymmetry overload control needs.

    Deliberately per-event-loop state via `asyncio.Condition`, created lazily,
    so importing this module never touches a loop.
    """

    def __init__(
        self,
        initial: int = 24,
        min_limit: int = 4,
        max_limit: int = 64,
        decrease_factor: float = 0.7,
        name: str = "upstream",
    ):
        self._limit = float(initial)
        self.min_limit = min_limit
        self.max_limit = max_limit
        self.decrease_factor = decrease_factor
        self.name = name
        self._in_flight = 0
        self._cond: Optional[asyncio.Condition] = None
        self._cond_loop = None

    def _condition(self) -> asyncio.Condition:
        loop = asyncio.get_running_loop()
        # Rebind if we are on a different loop (tests, asyncio.run per call).
        if self._cond is None or self._cond_loop is not loop:
            self._cond = asyncio.Condition()
            self._cond_loop = loop
            self._in_flight = 0
        return self._cond

    @property
    def limit(self) -> int:
        return max(self.min_limit, int(self._limit))

    def record_success(self) -> None:
        if self._limit < self.max_limit:
            self._limit = min(self.max_limit, self._limit + _INCREASE_GAIN / max(1.0, self._limit))

    def record_overload(self) -> None:
        new = max(float(self.min_limit), self._limit * self.decrease_factor)
        if int(new) != int(self._limit):
            logger.warning(
                "limiter %s: overload, concurrency %d -> %d",
                self.name, int(self._limit), int(new),
            )
        self._limit = new

    class _Slot:
        def __init__(self, outer: "AdaptiveLimiter"):
            self.outer = outer
            self._counted = False

        async def __aenter__(self):
            outer = self.outer
            cond = outer._condition()
            deadline = time.monotonic() + _LIMITER_MAX_WAIT
            async with cond:
                while outer._in_flight >= outer.limit:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        # Congestion control must never become an unbounded
                        # queue. Q11's whole request budget is 18s; if the
                        # limit shrank under Q9's 32-wide batch and stayed
                        # low, a Q11 call could wait here indefinitely --
                        # LONGER than its own httpx timeout would ever allow,
                        # because the wait happens BEFORE that timeout even
                        # starts. Every caller already has its own hard
                        # timeout on the actual HTTP call; past this bound,
                        # proceeding over-limit and letting THAT timeout
                        # govern is strictly better than starving the caller
                        # here where nothing bounds the wait at all.
                        logger.warning(
                            "limiter %s: %.1fs wait exceeded, admitting over limit (%d/%d)",
                            outer.name, _LIMITER_MAX_WAIT, outer._in_flight, outer.limit,
                        )
                        break
                    try:
                        await asyncio.wait_for(cond.wait(), timeout=remaining)
                    except asyncio.TimeoutError:
                        break
                outer._in_flight += 1
                self._counted = True
            return outer

        async def __aexit__(self, *exc):
            outer = self.outer
            cond = outer._condition()
            async with cond:
                if self._counted:
                    outer._in_flight -= 1
                cond.notify(1)
            return False

    def slot(self) -> "_Slot":
        return self._Slot(self)

    def snapshot(self) -> dict:
        return {"limit": self.limit, "inFlight": self._in_flight}


# ---------------------------------------------------------------------------
# Process-wide instances guarding the AIPipe upstream
# ---------------------------------------------------------------------------
AIPIPE_BREAKER = CircuitBreaker(
    failure_threshold=int(os.getenv("AIPIPE_BREAKER_THRESHOLD", "12")),
    recovery_time=float(os.getenv("AIPIPE_BREAKER_RECOVERY", "5")),
    name="aipipe",
)

AIPIPE_LIMITER = AdaptiveLimiter(
    initial=int(os.getenv("AIPIPE_CONCURRENCY_INITIAL", "24")),
    min_limit=int(os.getenv("AIPIPE_CONCURRENCY_MIN", "4")),
    max_limit=int(os.getenv("AIPIPE_CONCURRENCY_MAX", "64")),
    name="aipipe",
)


def resilience_snapshot() -> dict:
    return {"breaker": AIPIPE_BREAKER.snapshot(), "limiter": AIPIPE_LIMITER.snapshot()}
