import hashlib
import json
import os
from pathlib import Path


class DiskCache:
    def __init__(self, directory):
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def make_key(model, messages, params):
        payload = json.dumps(
            {"model": model, "messages": messages, "params": params},
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, key):
        path = self.dir / f"{key}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))["response"]

    def set(self, key, value):
        path = self.dir / f"{key}.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"response": value}), encoding="utf-8")
        os.replace(tmp, path)  # atomic: no half-written cache files
