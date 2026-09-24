import json
import time
from datetime import date
from pathlib import Path

import requests

HANDLE = input("Enter handle: ")
BASE = "https://codeforces.com/api"


_last_call_time = 0


def fetch(endpoint, params=None):
    global _last_call_time
    elasped = time.time() - _last_call_time
    if elasped < 2.2:
        time.sleep(2.2 - elasped)

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
        page = fetch(
            "user.status", {"handle": handle, "from": from_idx, "count": page_size}
        )
        all_submissions.extend(page)
        if len(page) != page_size:
            break
        from_idx += page_size

    return all_submissions


def fetch_rating(handle):
    return fetch("user.rating", {"handle": handle})


def fetch_problemset():
    return fetch("problemset.problems", {})


def save_raw(endpoint, handle, data):
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    fname = f"data/raw/{date.today()}_{endpoint}_{handle}.json"
    with open(fname, "w") as f:
        json.dump(data, f)
    print(f"Saved {fname}")


if __name__ == "__main__":
    # status = fetch("user.status", {"handle": HANDLE})
    status = fetch_all_status(HANDLE)
    rating = fetch_rating(HANDLE)
    problemset = fetch_problemset()
    save_raw("user.status", HANDLE, status)
    save_raw("user.rating", HANDLE, rating)
    save_raw("problemset.problems", HANDLE, problemset)
