# Data structures for contests
tags: data structures

## Choosing the right container
Most Div. 2 problems need only standard containers. Use a stack for matching brackets and "nearest smaller element to the left" (monotonic stack, O(n) total). Use a queue for BFS and a deque for sliding-window maximum. Use std::set or multiset when you need sorted order with insertions and deletions in O(log n), for example finding the closest available value with lower_bound. Use map or unordered_map for counting frequencies of large values. Use a priority_queue to repeatedly take the largest or smallest element, as in greedy scheduling and Dijkstra.

## Monotonic stack
A monotonic stack keeps indices whose values are increasing (or decreasing). For each new element, pop while the top is greater than or equal to it; the remaining top is the nearest smaller element to the left. Every index is pushed and popped once, so the total is O(n). It solves the largest rectangle in a histogram, the next greater element, and counting subarrays where a[i] is the minimum. When a brute force is O(n^2) because each element looks left for the nearest smaller value, a monotonic stack usually makes it linear.

## Segment tree and Fenwick tree basics
When you need both updates and range queries, prefix sums are not enough. A Fenwick tree (binary indexed tree) supports point update and prefix sum in O(log n) with about ten lines of code. A segment tree supports any associative operation such as sum, min, max or gcd over a range, with point updates in O(log n), and lazy propagation adds range updates. Around rating 1400 to 1600 these appear in problems like counting inversions or answering queries online.

## Common mistakes with data structures
Calling erase(value) on a multiset removes all copies; use erase(find(value)) to remove one. Accessing m[key] on a map inserts a default value, which can change size() and slow things down; use find or count to check membership. unordered_map can be hacked with anti-hash tests on Codeforces, so prefer map or add a custom hash. Iterating over a container while erasing from it invalidates iterators unless you use the iterator returned by erase.
