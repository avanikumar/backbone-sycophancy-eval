import httpx

from .base import Provider


class OpenAICompatProvider(Provider):
    def __init__(self, base_url: str, model: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key

    async def complete(self, messages, **params) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "messages": messages, **params},
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
