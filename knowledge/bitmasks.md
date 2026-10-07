# Bit manipulation
tags: bitmasks

## Bit operations you need
Use AND, OR, XOR and shifts to work with bits: x & (1 << i) tests bit i, x | (1 << i) sets it, x ^ (1 << i) flips it, and x & (x - 1) removes the lowest set bit. __builtin_popcount counts set bits (use the ll version for long long). XOR facts solve many problems: a ^ a = 0, a ^ 0 = a, XOR is commutative, so XOR of an array cancels pairs, and prefix XOR gives any range XOR in O(1).

## Iterating over subsets
A bitmask of n bits represents a subset of n items, so for n up to about 20 you can enumerate all 2^n subsets with a loop from 0 to (1 << n) - 1. Bitmask DP stores dp[mask] for subsets, as in the travelling salesman problem (dp[mask][last]) in O(2^n n^2). Submasks of a mask can be enumerated with s = (s - 1) & mask, and doing that for all masks totals O(3^n).

## Thinking bit by bit
Many problems with AND, OR or XOR become easy when you treat each bit independently, because these operations do not carry between bits. Ask what happens to bit 30, then bit 29, and so on; greedy from the highest bit down often gives the maximum XOR or OR. For sums of XOR over all pairs, count for each bit how many numbers have it set (c) and add c * (n - c) * 2^bit. Remember that 1 << 31 overflows int, so write 1LL << i for large shifts.
