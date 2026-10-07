# Notes

## Cohort rule (settled)
- Source: rated participants of the 3 most recent finished Div. 2 contests (`contest.ratingChanges`).
- Rating filter: rating right after that contest in 800–1600.
- Order: seeded random shuffle (`--seed`, default 0), then the first 25 handles that pass the skip rule.
- Skip rule: skip anyone with **< 5 rated contests OR < 50 solved problems**, so everyone kept has
  enough history for per-tag numbers to mean something. (The first draft said "and"; "or" is the
  stricter, intended version.)

## Why not "first handles in standings order"
Tried it first. The top of the standings in the 800–1600 range is dominated by new or alt accounts
(a big rating jump from a low starting rating), and the skip rule rejected almost all of them: 2 kept
after ~15 minutes of API calls. The few kept had an unusually good contest, which biases the
baseline. A seeded shuffle of everyone in range is representative and still reproducible.

## What the cohort is for
`cohort_baseline.json` holds per-tag average solve rate and wrong submits (mean of per-user means,
tags with >= 3 users). The profiler compares a user's tag against it, so a tag that is hard for
everyone (e.g. dp) isn't flagged just for being hard. It holds no handles.
