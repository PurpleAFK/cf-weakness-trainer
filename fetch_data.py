"""Codeforces API client: rate-limited calls, pagination, and raw JSON snapshots.

Usage:  python fetch_data.py <handle>
"""

import argparse
import json
import time
from datetime import date
from pathlib import Path

import requests

BASE = "https://codeforces.com/api"


_last_call_time = 0


def fetch(endpoint, params=None):
    global _last_call_time
    elapsed = time.time() - _last_call_time
    if elapsed < 2.2:
        time.sleep(2.2 - elapsed)

    url = f"{BASE}/{endpoint}"
    resp = requests.get(url, params=params, timeout=30)
    _last_call_time = time.time()

    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "OK":
        raise RuntimeError(f"API error: {data.get('comment')}")
    return data["result"]


def fetch_all_status(handle, page_size=100):
    all_submissions = []
    from_idx = 1
    while True:
        page = fetch("user.status", {"handle": handle, "from": from_idx, "count": page_size})
        all_submissions.extend(page)
        if len(page) != page_size:
            break
        from_idx += page_size

    return all_submissions


def fetch_rating(handle):
    return fetch("user.rating", {"handle": handle})


def fetch_problemset():
    return fetch("problemset.problems", {})


def fetch_user_info(handles):
    """Current rating etc. for many handles in one call (the API takes a ;-separated list)."""
    return fetch("user.info", {"handles": ";".join(handles)})


def save_raw(endpoint, handle, data, raw_dir="data/raw"):
    Path(raw_dir).mkdir(parents=True, exist_ok=True)
    fname = f"{raw_dir}/{date.today()}_{endpoint}_{handle}.json"
    with open(fname, "w") as f:
        json.dump(data, f)
    print(f"Saved {fname}")
    return fname


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handle")
    args = parser.parse_args()

    save_raw("user.status", args.handle, fetch_all_status(args.handle))
    save_raw("user.rating", args.handle, fetch_rating(args.handle))
    save_raw("problemset.problems", "all", fetch_problemset())  # not per-user


if __name__ == "__main__":
    main()
