# Graphs: BFS and DFS
tags: graphs, dfs and similar

## Representing a graph
Store a graph as an adjacency list: vector<vector<int>> adj(n), and for each edge (u, v) push v into adj[u] and u into adj[v] if the graph is undirected. This uses O(n + m) memory and lets you iterate a vertex's neighbors quickly. Grids are graphs too: each cell is a vertex and its neighbors are the four adjacent cells, which you can loop over with direction arrays dx and dy. An adjacency matrix only makes sense for small n, around 1000 or less.

## Depth-first search
DFS goes as deep as possible before backtracking, using recursion or an explicit stack. It finds connected components (run DFS from every unvisited vertex and count the runs), detects cycles, checks whether a graph is bipartite by two-coloring, and computes subtree information on trees. Each vertex and edge is processed once, so DFS is O(n + m). Recursive DFS can overflow the stack on a path of 1e5 or more vertices with some compilers; an iterative version avoids that.

## Breadth-first search and shortest paths in unweighted graphs
BFS visits vertices in order of distance from the source using a queue, so the first time it reaches a vertex is along a shortest path when every edge has the same weight. Use it for the minimum number of moves on a grid, the shortest chain of transformations, and distances from many sources at once (multi-source BFS: push all sources into the queue at distance 0). Keep a dist array initialized to -1 to mark unvisited vertices. With 0 and 1 edge weights, a deque-based 0-1 BFS still runs in O(n + m).

## Common mistakes in graph problems
Forgetting to reset visited arrays between test cases is the most common bug in multi-test problems. Vertices are often numbered from 1 in the input, so subtract one or size arrays n + 1. For grids, check bounds before reading a cell. Read the statement for whether the graph is directed, may contain self-loops or multiple edges, or may be disconnected. Recursive DFS on deep graphs needs care with stack size.

## How to practice graphs
Begin with counting components and BFS on grids, which appear often at ratings 1100 to 1400. Then do bipartite checking, cycle detection, and topological sort. The CSES graph section is an excellent ordered problem set. For each problem, first decide what the vertices and edges are; modeling the graph correctly is usually harder than running BFS or DFS.
