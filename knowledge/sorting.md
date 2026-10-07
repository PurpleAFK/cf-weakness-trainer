# Sorting
tags: sortings

## Sorting as a first step
Sorting in O(n log n) often makes a problem simple: after sorting, equal elements are adjacent, the closest pair of values is adjacent, and you can use two pointers or binary search. Sort pairs to process events in order (start and end of intervals), or sort indices by value while keeping the original positions for the output. Ask whether the order of the input matters; if it does not, sorting is almost free.

## Custom comparators and their pitfalls
Sort by a custom key with a comparator or a lambda. A comparator must define a strict weak ordering: it must return false for equal elements, so use a < b, never a <= b, or std::sort can crash or loop. To sort strings so their concatenation is smallest, compare a + b with b + a. For stable ordering of equal keys, use stable_sort. Counting sort works in O(n + k) when values are small integers.

## Exchange arguments for sorting orders
When the answer depends on the order of processing items, compare two adjacent items i and j: which order, i before j or j before i, gives a better result? If the comparison reduces to a rule based on each item alone, sort by that rule. This is how the classic scheduling problems are solved, and it is the proof technique behind many greedy-by-sorting solutions.
