from backbone.cache import DiskCache
from backbone.runner import Runner

MSGS = [{"role": "user", "content": "hi"}]


class FakeProvider:
    model = "fake"

    def __init__(self, fail_first=0):
        self.calls = 0
        self.fail_first = fail_first

    async def complete(self, messages, **params):
        self.calls += 1
        if self.calls <= self.fail_first:
            raise RuntimeError("boom")
        return "Canberra"


async def test_second_call_hits_cache(tmp_path):
    p = FakeProvider()
    r = Runner(p, DiskCache(tmp_path))
    assert await r.complete(MSGS) == "Canberra"
    assert await r.complete(MSGS) == "Canberra"
    assert p.calls == 1


async def test_retries_then_succeeds(tmp_path):
    p = FakeProvider(fail_first=2)
    r = Runner(p, DiskCache(tmp_path), backoff_base=0)
    assert await r.complete(MSGS) == "Canberra"
    assert p.calls == 3
