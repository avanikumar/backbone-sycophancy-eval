import httpx
import pytest

from backbone.cache import DiskCache
from backbone.runner import Runner

MSGS = [{"role": "user", "content": "hi"}]


def status_error(code):
    req = httpx.Request("POST", "http://x")
    return httpx.HTTPStatusError("err", request=req, response=httpx.Response(code, request=req))


class FakeProvider:
    model = "fake"

    def __init__(self, fail_first=0, exc=None):
        self.calls = 0
        self.fail_first = fail_first
        self.exc = exc or httpx.ConnectError("boom")

    async def complete(self, messages, **params):
        self.calls += 1
        if self.calls <= self.fail_first:
            raise self.exc
        return "Canberra"


async def test_second_call_hits_cache(tmp_path):
    p = FakeProvider()
    r = Runner(p, DiskCache(tmp_path))
    assert await r.complete(MSGS) == "Canberra"
    assert await r.complete(MSGS) == "Canberra"
    assert p.calls == 1


async def test_retries_network_error_then_succeeds(tmp_path):
    p = FakeProvider(fail_first=2)
    r = Runner(p, DiskCache(tmp_path), backoff_base=0)
    assert await r.complete(MSGS) == "Canberra"
    assert p.calls == 3


async def test_retries_rate_limit_then_succeeds(tmp_path):
    p = FakeProvider(fail_first=1, exc=status_error(429))
    r = Runner(p, DiskCache(tmp_path), backoff_base=0)
    assert await r.complete(MSGS) == "Canberra"
    assert p.calls == 2


async def test_does_not_retry_auth_error(tmp_path):
    p = FakeProvider(fail_first=5, exc=status_error(401))
    r = Runner(p, DiskCache(tmp_path), backoff_base=0)
    with pytest.raises(httpx.HTTPStatusError):
        await r.complete(MSGS)
    assert p.calls == 1
