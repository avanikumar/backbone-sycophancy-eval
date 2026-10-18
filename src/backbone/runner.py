import asyncio

import httpx


def _is_transient(exc: Exception) -> bool:
    """Retry only errors that can succeed later: 429, 5xx, network problems."""
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        return code == 429 or code >= 500
    return isinstance(exc, httpx.TransportError)


class Runner:
    def __init__(self, provider, cache, concurrency=5, max_retries=4,
                 backoff_base=1.0, params=None):
        self.provider = provider
        self.cache = cache
        self.sem = asyncio.Semaphore(concurrency)
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.params = params or {}

    async def complete(self, messages):
        key = self.cache.make_key(self.provider.model, messages, self.params)
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        async with self.sem:  # limits simultaneous API calls
            for attempt in range(self.max_retries + 1):
                try:
                    out = await self.provider.complete(messages, **self.params)
                    break
                except Exception as exc:
                    if attempt == self.max_retries or not _is_transient(exc):
                        raise
                    delay = self.backoff_base * 2**attempt
                    if isinstance(exc, httpx.HTTPStatusError):
                        retry_after = exc.response.headers.get("retry-after")
                        if retry_after:
                            try:
                                delay = max(delay, float(retry_after))
                            except ValueError:
                                pass
                    await asyncio.sleep(delay)
        self.cache.set(key, out)
        return out
