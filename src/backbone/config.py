import yaml
from pydantic import BaseModel


class Config(BaseModel):
    base_url: str
    model: str
    api_key_env: str
    dataset: str
    cache_dir: str = ".cache"
    concurrency: int = 5
    max_retries: int = 6
    backoff_base: float = 2.0
    temperature: float = 0.0
    max_tokens: int = 100
    system_prompt: str | None = None


def load_config(path) -> Config:
    with open(path, encoding="utf-8") as f:
        return Config(**yaml.safe_load(f))
