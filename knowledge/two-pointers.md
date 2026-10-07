# Two pointers and sliding window
tags: two pointers

## The two pointers technique
Two pointers walks two indices through an array, usually both moving only forward, so the total work is O(n) instead of O(n^2). It works when moving one pointer never requires moving the other one back. Classic uses: finding a pair with a given sum in a sorted array (one pointer at each end, move the one that brings the sum closer), merging two sorted arrays, and removing duplicates in place. Sorting first is often what makes two pointers possible.

## Sliding window
A sliding window keeps a segment [l, r] that satisfies a condition. Extend r one step at a time, and while the window becomes invalid, move l forward. This answers questions like the longest subarray with sum at most S (non-negative numbers), the longest substring without repeated characters, or the number of subarrays with at most k distinct values, all in O(n). The window needs a cheap way to update its state when an element enters or leaves: a running sum, a frequency array or a map of counts.

## Common mistakes with two pointers
Sliding window on sums only works when all numbers are non-negative; with negative numbers the window condition is no longer monotonic and you need prefix sums with a map or another approach. Forgetting to update the window state when the left pointer moves is the most common bug. When counting subarrays, add r - l + 1 for each r, which counts all valid windows ending at r. Check that the left pointer never passes the right one.

## How to practice two pointers
Solve a few problems that are explicitly about pairs in sorted arrays, then several "longest or shortest subarray such that" problems. Before coding, state why the left pointer never has to move back. Two pointers often appears together with sorting and binary search, so if a binary search solution is O(n log n), check whether two pointers gives O(n).
