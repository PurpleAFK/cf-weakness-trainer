"""Find and load the raw JSON snapshots that fetch_data.py writes to data/raw/."""

import json
from pathlib import Path


def latest_snapshot(endpoint, handle="*", raw_dir="data/raw"):
    """Newest file named <date>_<endpoint>_<handle>.json (ISO dates sort as strings)."""
    matches = sorted(Path(raw_dir).glob(f"*_{endpoint}_{handle}.json"))
    if not matches:
        raise FileNotFoundError(f"no {endpoint} snapshot for {handle} in {raw_dir}")
    return matches[-1]


def load_json(path):
    with open(path) as f:
        return json.load(f)
