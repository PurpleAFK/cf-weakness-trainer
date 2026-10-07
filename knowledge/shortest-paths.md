# Shortest paths
tags: shortest paths, graphs

## Dijkstra's algorithm
Dijkstra finds shortest paths from one source when all edge weights are non-negative. Keep a priority queue of (distance, vertex) pairs, always pop the closest unfinished vertex, and relax its edges: if dist[u] + w < dist[v], update dist[v] and push it. Skip popped entries whose distance is larger than the stored one (lazy deletion). The complexity is O((n + m) log n). Use long long distances and initialize them to a large value such as 1e18.

## Other shortest path algorithms
Use BFS when all weights are equal, 0-1 BFS when weights are 0 or 1, and Dijkstra for general non-negative weights. Bellman-Ford handles negative weights and detects negative cycles in O(n m). Floyd-Warshall computes all-pairs shortest paths in O(n^3) and fits when n is at most about 400. Choosing the right algorithm from the constraints is a common interview question as well as a contest skill.

## Modeling tricks for shortest path problems
Many problems become shortest path problems after adding information to the vertex. If you may use a coupon once, make a state (vertex, used) and run Dijkstra on the doubled graph. To find shortest paths to a single target in a directed graph, reverse all edges and run from the target. To count shortest paths, keep a ways array and add counts when you find an equal distance. Mistakes to avoid: using int for distances, and running Dijkstra with negative edges.
