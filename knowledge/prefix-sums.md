# Prefix sums and difference arrays
tags: data structures, implementation

## Prefix sums for range queries
A prefix sum array p where p[i] = a[0] + ... + a[i-1] answers any range sum a[l..r] as p[r+1] - p[l] in O(1) after O(n) preprocessing. The same idea works for counts (how many vowels in a substring), XOR, and two dimensions, where a rectangle sum uses inclusion-exclusion of four prefix values. Use long long because sums overflow int quickly. Prefix sums are the first tool to try whenever a problem asks many questions about subarrays.

## Difference arrays for range updates
A difference array d with d[i] = a[i] - a[i-1] turns "add v to every element in [l, r]" into two O(1) operations: d[l] += v and d[r+1] -= v. After all updates, a prefix sum over d rebuilds the final array. This handles many offline range updates in O(n + q). Combined with sorting events, it also counts how many intervals cover each point, a frequent pattern in Div. 2 B and C problems.

## Subarray counting with prefix sums and a map
The number of subarrays with sum exactly k equals the number of pairs i < j with p[j] - p[i] = k. Walk j from left to right, add the count of p[j] - k already seen (stored in a map), then record p[j]. This works with negative numbers, unlike a sliding window. The same trick counts subarrays whose sum is divisible by m, by storing prefix sums modulo m.
