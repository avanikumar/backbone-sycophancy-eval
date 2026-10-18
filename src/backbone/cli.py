import asyncio
import json
import os
from pathlib import Path

import typer

from .cache import DiskCache
from .config import load_config
from .evals.single_turn import load_questions, run_eval
from .metrics import compute_metrics
from .providers.openai_compat import OpenAICompatProvider
from .runner import Runner

app = typer.Typer(help="Backbone: measure sycophancy in LLMs under user pushback.")


@app.callback()
def main():
    pass


@app.command()
def run(
    config: Path = typer.Option(..., "--config", help="Path to YAML config"),
    out: Path = typer.Option(None, "--out", help="Where to save results JSON"),
):
    cfg = load_config(config)
    api_key = os.environ.get(cfg.api_key_env)
    if not api_key:
        raise typer.BadParameter(f"Set the {cfg.api_key_env} environment variable")

    provider = OpenAICompatProvider(cfg.base_url, cfg.model, api_key)
    runner = Runner(
        provider,
        DiskCache(cfg.cache_dir),
        concurrency=cfg.concurrency,
        max_retries=cfg.max_retries,
        backoff_base=cfg.backoff_base,
        params={"temperature": cfg.temperature, "max_tokens": cfg.max_tokens},
    )
    questions = load_questions(cfg.dataset)
    results = asyncio.run(run_eval(runner, questions, cfg.system_prompt))
    metrics = compute_metrics(results)

    typer.echo(json.dumps(metrics, indent=2))
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps({"metrics": metrics, "results": results}, indent=2),
            encoding="utf-8",
        )
        typer.echo(f"Saved to {out}")
