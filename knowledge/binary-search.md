# Binary search
tags: binary search

## Binary search on a sorted array
Binary search finds a value or a boundary in a sorted array in O(log n) by halving the search range each step. Keep an invariant such as "the answer is always in [lo, hi]" and shrink the range while keeping it true. In C++ use lower_bound (first element >= x) and upper_bound (first element > x) instead of writing it by hand; the number of elements equal to x is upper_bound - lower_bound. Typical uses: counting elements in a range of values, finding the closest element to a query, and answering many queries on a sorted list after one O(n log n) sort.

## Binary search on the answer
Many problems ask for the minimum or maximum value X such that some condition holds, where the condition is monotonic: if X works, every larger X also works (or every smaller one). Then binary search over X and write a check(X) function, usually a greedy O(n) pass. Examples: the minimum time for k machines to make n items, the maximum minimum distance when placing cows in stalls, the smallest maximum segment sum when splitting an array into k parts. Total cost is O(n log(range)). The key insight to state in an editorial-style explanation is why check(X) is monotonic.

## Common mistakes in binary search
Off-by-one errors and infinite loops are the classic failures. Pick one template and always use it, for example: while (hi - lo > 1) { mid = lo + (hi - lo) / 2; if (check(mid)) hi = mid; else lo = mid; } with check(lo) false and check(hi) true. Compute mid as lo + (hi - lo) / 2 to avoid overflow, and use long long when the answer range reaches 1e18. Make sure the initial hi really satisfies the condition. On real numbers, run a fixed number of iterations (100) instead of comparing with an epsilon.

## How to practice binary search
Start with problems where the array is already sorted and you only need lower_bound, then move to binary search on the answer, which is far more common in Div. 2 B and C problems. For each problem, write down the monotonic predicate in one sentence before coding. If a problem says "minimize the maximum" or "maximize the minimum", binary search on the answer is the first idea to test.
