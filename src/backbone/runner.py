import asyncio


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
                except Exception:
                    if attempt == self.max_retries:
                        raise
                    await asyncio.sleep(self.backoff_base * 2**attempt)
        self.cache.set(key, out)
        return out
