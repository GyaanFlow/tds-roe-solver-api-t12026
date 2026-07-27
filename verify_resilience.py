"""Tests for the shared-upstream resilience layer (T22026/GA4/resilience.py).

These assert the properties that matter on a MULTI-TENANT hub, where one
caller's problem must never become everyone's problem.
"""

import asyncio
import statistics

import pytest

from T22026.GA4.resilience import (
    AdaptiveLimiter,
    CircuitBreaker,
    backoff_delay,
)


# ---------------------------------------------------------------------------
# Jittered backoff
# ---------------------------------------------------------------------------
def test_backoff_is_jittered_not_synchronised():
    """The old linear backoff woke 64 dossiers at the identical instant."""
    delays = [backoff_delay(0) for _ in range(200)]
    assert len(set(delays)) > 150, "delays must not be identical (thundering herd)"
    assert statistics.pstdev(delays) > 0.05, "needs real spread"


def test_backoff_grows_exponentially_and_is_capped():
    # Sample the max of many draws to see the window, since it is full-jitter.
    w0 = max(backoff_delay(0, base=0.5, cap=8.0) for _ in range(400))
    w3 = max(backoff_delay(3, base=0.5, cap=8.0) for _ in range(400))
    assert w3 > w0, "window must widen with attempt number"
    assert all(backoff_delay(50, base=0.5, cap=8.0) <= 8.0 for _ in range(200)), "cap"
    assert all(backoff_delay(i) >= 0 for i in range(10) for _ in range(20))


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------
def test_breaker_opens_after_threshold_and_fails_fast():
    cb = CircuitBreaker(failure_threshold=3, recovery_time=60.0)
    assert cb.allows_request()
    for _ in range(3):
        cb.record_failure()
    assert cb.state == CircuitBreaker.OPEN
    assert not cb.allows_request(), "open breaker must reject immediately"


def test_breaker_self_heals_without_intervention():
    """The whole point: recovery is automatic."""
    cb = CircuitBreaker(failure_threshold=2, recovery_time=0.05)
    cb.record_failure()
    cb.record_failure()
    assert not cb.allows_request()

    import time
    time.sleep(0.06)  # recovery window elapses

    assert cb.state == CircuitBreaker.HALF_OPEN
    # A small BURST of probes, not one: with a single probe every other caller
    # arriving in the same millisecond is refused while it is still in flight,
    # so a recovered upstream still serves almost nothing.
    for _ in range(cb.half_open_probes):
        assert cb.allows_request(), "probe budget admitted"
    assert not cb.allows_request(), "probe budget is bounded"

    cb.record_success()
    assert cb.state == CircuitBreaker.CLOSED
    assert cb.allows_request()


def test_recovery_is_not_a_stampede():
    """REGRESSION: found by chaos test. When the upstream recovered, every
    waiting caller checked at once, a few became probes and the REST WERE
    REFUSED -- so a perfectly healthy upstream still served 1 request out of
    60. Callers must be able to wait briefly for the breaker to close."""
    cb = CircuitBreaker(failure_threshold=1, recovery_time=0.1, half_open_probes=2)
    cb.record_failure()
    assert not cb.allows_request()

    async def caller(i):
        # Everyone arrives while the breaker is still OPEN.
        got = await cb.wait_until_available(max_wait=3.0)
        if got:
            cb.record_success()   # upstream is healthy again
        return got

    async def run():
        return await asyncio.gather(*[caller(i) for i in range(60)])

    results = asyncio.run(run())
    admitted = sum(1 for r in results if r)
    assert admitted == 60, "only %d of 60 got through after recovery" % admitted


def test_unresolved_probes_cannot_deadlock_the_breaker_forever():
    """REGRESSION: a probe is admitted by allows_request() and released only by
    record_success/record_failure/release_probe. Paths that returned without
    scoring an outcome (401/403, 429) leaked the slot, and once every slot
    leaked the breaker sat in HALF_OPEN refusing EVERY request permanently --
    nothing is time-based out of HALF_OPEN. A hub-wide outage caused by three
    students with expired tokens."""
    import time

    # Margins widened from an earlier 0.05/0.06s pairing that flaked under
    # system load -- these need headroom, not tight timing precision.
    cb = CircuitBreaker(failure_threshold=1, recovery_time=0.05, half_open_probes=3)
    cb._probe_timeout = 0.3
    cb.record_failure()
    time.sleep(0.15)

    for _ in range(3):                       # admit every probe...
        assert cb.allows_request()
    assert not cb.allows_request(), "budget consumed"

    time.sleep(0.45)                          # ...and never resolve them
    assert cb.allows_request(), "stale probes must be reclaimed, not wedged forever"


def test_release_probe_returns_the_slot():
    """The explicit path, so we do not depend on the timeout safety net."""
    import time

    cb = CircuitBreaker(failure_threshold=1, recovery_time=0.05, half_open_probes=2)
    cb.record_failure()
    time.sleep(0.06)

    assert cb.allows_request()
    assert cb.allows_request()
    assert not cb.allows_request(), "budget consumed"

    cb.release_probe()
    assert cb.allows_request(), "released slot must be reusable immediately"
    assert cb.state == CircuitBreaker.HALF_OPEN, "release must not score an outcome"


def test_expired_tokens_cannot_wedge_the_hub():
    """End-to-end: repeated 401s while the breaker is HALF_OPEN must leave it
    usable for everybody else."""
    import time

    import T22026.GA4.solvers as solvers
    from T22026.GA4.resilience import AIPIPE_BREAKER

    from T22026.GA4.solvers import TokenExpiredError

    AIPIPE_BREAKER.record_failure()  # force OPEN
    AIPIPE_BREAKER._state = CircuitBreaker.OPEN
    AIPIPE_BREAKER._opened_at = time.monotonic() - 999  # window already elapsed

    class FakeResp:
        status_code = 401
        text = "bad token"

    class FakeClient:
        async def post(self, *a, **k):
            return FakeResp()

    orig = solvers._get_http_client
    solvers._get_http_client = lambda: FakeClient()

    async def run():
        for i in range(10):  # more than the probe budget
            with pytest.raises(TokenExpiredError):
                await solvers.aipipe_chat(
                    [{"role": "user", "content": "tok-%d" % i}], "bad", retries=1, timeout=0.4
                )

    try:
        asyncio.run(run())
        assert AIPIPE_BREAKER.allows_request(), (
            "hub wedged: expired tokens consumed the whole probe budget"
        )
    finally:
        solvers._get_http_client = orig
        AIPIPE_BREAKER.record_success()


def test_breaker_reopens_if_probe_fails():
    cb = CircuitBreaker(failure_threshold=1, recovery_time=0.05)
    cb.record_failure()
    import time
    time.sleep(0.06)
    assert cb.allows_request()      # probe
    cb.record_failure()             # probe fails
    assert cb.state == CircuitBreaker.OPEN
    assert not cb.allows_request()


def test_success_resets_failure_run():
    cb = CircuitBreaker(failure_threshold=3, recovery_time=60.0)
    cb.record_failure()
    cb.record_failure()
    cb.record_success()
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitBreaker.CLOSED, "must count CONSECUTIVE failures"


# ---------------------------------------------------------------------------
# Multi-tenant safety -- the property that matters most
# ---------------------------------------------------------------------------
def test_one_students_bad_token_cannot_open_the_shared_circuit():
    """401/403 and 429 are per-caller faults. If they tripped the shared
    breaker, a single student with an expired token or exhausted quota would
    take the API down for every other student on the hub."""
    import T22026.GA4.solvers as solvers
    from T22026.GA4.resilience import AIPIPE_BREAKER

    AIPIPE_BREAKER.record_success()  # start closed
    calls = {"n": 0}

    class FakeResp:
        status_code = 429
        text = "quota exceeded"

    class FakeClient:
        async def post(self, *a, **k):
            calls["n"] += 1
            return FakeResp()

    orig = solvers._get_http_client
    solvers._get_http_client = lambda: FakeClient()

    async def run():
        for i in range(40):  # far beyond the breaker threshold
            with pytest.raises(RuntimeError):
                await solvers.aipipe_chat(
                    [{"role": "user", "content": "quota-%d" % i}], "tok", retries=1
                )

    try:
        asyncio.run(run())
        assert AIPIPE_BREAKER.state == CircuitBreaker.CLOSED, (
            "429 (one caller's quota) must NOT open the shared breaker"
        )
        assert calls["n"] == 40, "every call still attempted"
    finally:
        solvers._get_http_client = orig
        AIPIPE_BREAKER.record_success()


def test_upstream_5xx_DOES_open_the_shared_circuit():
    """The complement: a genuinely sick upstream must trip it, so hundreds of
    concurrent calls fail fast instead of each burning a full timeout."""
    import T22026.GA4.solvers as solvers
    from T22026.GA4.resilience import AIPIPE_BREAKER

    AIPIPE_BREAKER.record_success()
    calls = {"n": 0}

    class FakeResp:
        status_code = 503
        text = "upstream down"

    class FakeClient:
        async def post(self, *a, **k):
            calls["n"] += 1
            return FakeResp()

    orig = solvers._get_http_client
    solvers._get_http_client = lambda: FakeClient()

    async def run():
        for i in range(30):
            with pytest.raises(RuntimeError):
                # small timeout => small circuit wait, keeps the test fast
                await solvers.aipipe_chat(
                    [{"role": "user", "content": "down-%d" % i}], "tok",
                    retries=1, timeout=0.4,
                )

    try:
        asyncio.run(run())
        assert AIPIPE_BREAKER.state == CircuitBreaker.OPEN, "5xx must open it"
        assert calls["n"] < 30, (
            "breaker must SHORT-CIRCUIT: %d calls still reached a dead upstream" % calls["n"]
        )
    finally:
        solvers._get_http_client = orig
        AIPIPE_BREAKER.record_success()


# ---------------------------------------------------------------------------
# AIMD adaptive concurrency
# ---------------------------------------------------------------------------
def test_limiter_backs_off_fast_and_recovers_slowly():
    lim = AdaptiveLimiter(initial=32, min_limit=4, max_limit=64)
    assert lim.limit == 32
    lim.record_overload()
    assert lim.limit < 32, "multiplicative decrease on overload"
    dropped = lim.limit
    for _ in range(5):
        lim.record_success()
    assert lim.limit <= dropped + 2, "additive increase must be gradual, not instant"


def test_limiter_never_exceeds_its_limit_concurrently():
    lim = AdaptiveLimiter(initial=5, min_limit=5, max_limit=5)
    peak = {"v": 0}
    cur = {"v": 0}

    async def worker():
        async with lim.slot():
            cur["v"] += 1
            peak["v"] = max(peak["v"], cur["v"])
            await asyncio.sleep(0.01)
            cur["v"] -= 1

    async def run():
        await asyncio.gather(*[worker() for _ in range(60)])

    asyncio.run(run())
    assert peak["v"] <= 5, "limiter admitted %d > 5" % peak["v"]
    assert cur["v"] == 0, "all slots released"


def test_limiter_releases_slot_on_exception():
    """A leaked slot would permanently shrink usable concurrency."""
    lim = AdaptiveLimiter(initial=2, min_limit=2, max_limit=2)
    done = []

    async def run():
        for _ in range(10):
            with pytest.raises(ValueError):
                async with lim.slot():
                    raise ValueError("boom")

        async def w():
            async with lim.slot():
                done.append(1)

        # If slots leaked, this would deadlock.
        await asyncio.wait_for(asyncio.gather(*[w() for _ in range(6)]), timeout=2.0)

    asyncio.run(run())
    assert len(done) == 6


def test_limiter_across_separate_asyncio_run_calls():
    """Module-global limiter reused across loops must not bind to a dead one."""
    lim = AdaptiveLimiter(initial=3, min_limit=3, max_limit=3)

    async def use():
        async with lim.slot():
            await asyncio.sleep(0)
            return True

    assert asyncio.run(use()) is True
    assert asyncio.run(use()) is True, "must rebind cleanly to the new loop"


def test_limiter_wait_is_bounded_not_unbounded():
    """REGRESSION: this hub runs Q9 (up to 32-wide batches, 55s/request), Q10
    (up to 16-wide, 45s/request) and Q11 (18s/request -- far tighter) through
    the SAME shared limiter. The original slot() had no wait timeout at all,
    so a Q11 call arriving while Q9's batch saturated the limiter could queue
    for however long that batch took -- already longer than Q11's entire
    request budget, and far longer than any per-call httpx timeout, because
    this wait happens BEFORE that timeout even starts. A caller must be
    admitted (over-limit if necessary) once its wait exceeds the bound,
    rather than starve indefinitely."""
    import time

    from T22026.GA4 import resilience as resilience_mod

    lim = AdaptiveLimiter(initial=1, min_limit=1, max_limit=1)
    orig_max_wait = resilience_mod._LIMITER_MAX_WAIT
    resilience_mod._LIMITER_MAX_WAIT = 0.2  # keep the test fast

    async def hog():
        async with lim.slot():
            await asyncio.sleep(5.0)  # simulate a long batch holding the only slot

    async def run():
        hog_task = asyncio.create_task(hog())
        await asyncio.sleep(0.02)  # let the hog take the slot first
        t = time.monotonic()
        async with lim.slot():
            waited = time.monotonic() - t
        hog_task.cancel()
        # Fully await the cancellation before the loop closes -- an
        # un-awaited cancelled task can log its CancelledError after this
        # test function returns, polluting whichever test runs next.
        try:
            await hog_task
        except asyncio.CancelledError:
            pass
        return waited

    try:
        waited = asyncio.run(run())
    finally:
        resilience_mod._LIMITER_MAX_WAIT = orig_max_wait
    assert waited < 1.0, "waited %.2fs -- congestion control must not queue past its own bound" % waited
