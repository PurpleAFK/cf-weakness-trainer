# Combinatorics and counting
tags: combinatorics, math

## Counting basics
The number of ways to choose k items from n is C(n, k) = n! / (k! (n-k)!). Precompute factorials and inverse factorials modulo a prime up to n once, then every C(n, k) is O(1). Rules to combine counts: multiply for independent choices made in sequence, add for disjoint cases. Stars and bars counts the ways to split n identical items into k groups: C(n + k - 1, k - 1). Pascal's rule C(n, k) = C(n-1, k-1) + C(n-1, k) gives an O(n^2) table when n is small.

## Counting techniques
Count the complement when the direct count is hard: total ways minus bad ways. Inclusion-exclusion counts the union of overlapping sets by alternately adding and subtracting intersections. Contribution technique: instead of enumerating all subarrays or pairs, count for each element how many of them it belongs to and add up its contribution; this turns O(n^2) sums over pairs into O(n). Double counting the same object from two sides is a frequent bug, so define exactly what is counted once.

## How to practice combinatorics
Verify every formula with a brute force on small inputs, because off-by-one errors in counting are easy to make and hard to see. Write the factorial and inverse factorial template once and keep it. Practice the contribution technique specifically, since it appears in many Div. 2 C and D problems about sums over all subarrays.
