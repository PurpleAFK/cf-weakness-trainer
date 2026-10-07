# Trees
tags: trees, dfs and similar

## Tree basics and traversal
A tree is a connected graph with n vertices and n - 1 edges and no cycles, so there is exactly one path between any two vertices. Root it at vertex 1 and run a DFS that passes the parent, so you never walk back up. In one DFS you can compute depth, parent, subtree size, and any value that combines children, such as the sum of a subtree. Process children first and then combine (post-order) for subtree answers.

## Tree DP and the diameter
Tree DP stores an answer for each subtree, for example dp[v][0 or 1] for the maximum independent set where v is or is not chosen, combining the children's values. The diameter (the longest path) can be found with two BFS or DFS runs: from any vertex find the farthest vertex a, then from a find the farthest vertex b; the distance from a to b is the diameter. Rerooting computes an answer for every possible root in O(n) by moving the root across each edge and updating the values.

## Common mistakes with trees
Deep recursion on a path-shaped tree with n = 2e5 can overflow the stack. The input may give edges without saying which end is the parent, so always root the tree yourself. Remember that a tree with n vertices has exactly n - 1 edges; a problem that says "graph with n - 1 edges, connected" is describing a tree. Reset adjacency lists between test cases.
