import pyrogram.methods.rate_limiter as rate_limiter
from pyrogram.methods.rate_limiter import AdaptiveBucket


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def make(monkeypatch, **kwargs):
    clock = Clock()
    monkeypatch.setattr(rate_limiter.time, "monotonic", clock)
    return AdaptiveBucket(rate=16, ceiling=100, burst=8, **kwargs), clock


def test_a_flood_lowers_the_rate_once_per_second(monkeypatch):
    bucket, clock = make(monkeypatch)

    for _ in range(8):
        bucket.on_flood()

    assert bucket.rate == 16 * 0.85

    clock.now += 1.0
    bucket.on_flood()

    assert bucket.rate == 16 * 0.85 * 0.85


def test_the_rate_never_drops_below_the_floor(monkeypatch):
    bucket, clock = make(monkeypatch, floor=2.0)

    for _ in range(100):
        clock.now += 1.0
        bucket.on_flood()

    assert bucket.rate == 2.0


def test_clean_seconds_raise_the_rate_up_to_the_ceiling(monkeypatch):
    bucket, clock = make(monkeypatch, step=0.5)

    for _ in range(8):
        bucket.on_success()

    assert bucket.rate == 16

    clock.now += 1.0
    bucket.on_success()

    assert bucket.rate == 16.5

    for _ in range(1000):
        clock.now += 1.0
        bucket.on_success()

    assert bucket.rate == 100


def test_no_raise_right_after_a_flood(monkeypatch):
    bucket, clock = make(monkeypatch)

    clock.now += 1.0
    bucket.on_flood()
    clock.now += 1.5
    bucket.on_success()

    assert bucket.rate == 16 * 0.85

    clock.now += 0.5
    bucket.on_success()

    assert bucket.rate == 16 * 0.85 + 0.5
