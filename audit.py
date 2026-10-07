"""Exploratory look at one user's submissions: verdicts, unique problems, missing ratings.

Usage:  python audit.py <handle>
"""

import argparse

import pandas as pd

from snapshots import latest_snapshot, load_json


def audit(status):
    df = pd.DataFrame(status)
    print(df.shape)
    print(df["verdict"].value_counts())

    # each submission nests a "problem" dict; json_normalize flattens it into problem.* columns
    df_flat = pd.json_normalize(status)
    problems = df_flat[["problem.contestId", "problem.index", "problem.rating"]].drop_duplicates(
        subset=["problem.contestId", "problem.index"]
    )
    print(problems)
    print("problems with no rating:", problems["problem.rating"].isna().sum())
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handle")
    args = parser.parse_args()
    audit(load_json(latest_snapshot("user.status", args.handle)))


if __name__ == "__main__":
    main()
