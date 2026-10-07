# Disjoint set union
tags: dsu, graphs

## Disjoint set union (union-find)
A DSU keeps a partition of elements into groups and supports two operations: find(x) returns the representative of x's group, and unite(a, b) merges two groups. With path compression and union by size, both run in nearly constant amortized time. It answers "are these two vertices connected" while edges are being added, counts components, and tracks group sizes. It is about fifteen lines of code and worth memorizing.

## Where DSU appears
Kruskal's minimum spanning tree sorts edges by weight and adds each edge whose ends are in different groups. Offline connectivity problems process edges in a clever order, for example adding edges in decreasing weight to answer queries about thresholds, or reversing a sequence of deletions into additions. DSU also merges positions that must be equal, such as characters in a string that are forced to match. Common bug: calling find on the original element instead of the representative when merging sizes.
