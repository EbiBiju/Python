"""
Core algorithms for the Network Optimization prototype (DAA CIA3).

Problem: connect every location with the LEAST total cable, i.e. find a
Minimum Spanning Tree (MST) of a weighted, undirected graph.

Everything is written from scratch (no networkx here):
  * Kruskal's algorithm  - sort edges, add the cheapest one that does not
                           create a cycle (cycle check with Union-Find)
  * Prim's algorithm     - grow one tree outwards, always adding the cheapest
                           edge that reaches a new location (min-heap)

Graph format
    nodes : list of names
    edges : list of (a, b, weight)           (undirected)
    graph : {node: [(neighbour, weight), ...]}   (adjacency list, built from edges)
"""

import heapq
import random
import time


# --------------------------------------------------------------------------
# Union-Find (Disjoint Set Union) with path compression + union by rank
# --------------------------------------------------------------------------
class UnionFind:
    """
    Keeps track of which locations are already connected.
    find(x)      : which group does x belong to?
    union(a, b)  : merge two groups; returns False if a and b were already in
                   the same group (adding the edge would create a cycle).
    Amortised cost per operation: O(alpha(V)), practically constant.
    """

    def __init__(self, items):
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in items}

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:            # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:        # union by rank
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def build_graph(nodes, edges):
    """Adjacency list from an undirected edge list."""
    graph = {n: [] for n in nodes}
    for a, b, w in edges:
        graph[a].append((b, w))
        graph[b].append((a, w))
    return graph


def _check_weights(edges):
    for a, b, w in edges:
        if w < 0:
            raise ValueError(f"Negative weight on {a}-{b}. Use non-negative cable lengths/costs.")


# --------------------------------------------------------------------------
# 1. Kruskal's algorithm
# --------------------------------------------------------------------------
def kruskal(nodes, edges):
    """
    Returns (mst_edges, total_weight, steps, connected)

    steps : one record per edge examined, in sorted order:
            {"step", "edge": (a, b, w), "decision": "accepted" | "rejected (cycle)",
             "total": running total, "components": number of separate groups}
    connected : False if the graph is not connected (result is then a spanning forest).

    Time  : O(E log E) for the sort (= O(E log V)) + O(E * alpha(V)) for Union-Find
    Space : O(V + E)
    """
    _check_weights(edges)
    ordered = sorted(edges, key=lambda e: (e[2], e[0], e[1]))   # deterministic ties
    uf = UnionFind(nodes)
    mst, steps, total = [], [], 0
    components = len(nodes)

    for a, b, w in ordered:
        if uf.union(a, b):
            mst.append((a, b, w))
            total += w
            components -= 1
            decision = "accepted"
        else:
            decision = "rejected (cycle)"
        steps.append(
            {
                "step": len(steps) + 1,
                "edge": (a, b, w),
                "decision": decision,
                "total": total,
                "components": components,
            }
        )
        if len(mst) == len(nodes) - 1:        # tree complete: remaining edges can't help
            break

    connected = len(mst) == len(nodes) - 1
    return mst, total, steps, connected


# --------------------------------------------------------------------------
# 2. Prim's algorithm (binary min-heap)
# --------------------------------------------------------------------------
def prim(graph, start):
    """
    Returns (mst_edges, total_weight, steps, connected)

    steps : one record per location added to the tree:
            {"step", "added": node, "via": (parent, node, w) or None for the start,
             "total": running total, "frontier": number of candidate edges in the heap}
    connected : False if some locations cannot be reached from `start`.

    Time  : O((V + E) log V) with a binary heap
    Space : O(V + E)
    """
    for u, edges in graph.items():
        for v, w in edges:
            if w < 0:
                raise ValueError(f"Negative weight on {u}-{v}.")

    visited = {start}
    heap = [(w, start, v) for v, w in graph[start]]
    heapq.heapify(heap)
    mst, total = [], 0
    steps = [{"step": 1, "added": start, "via": None, "total": 0, "frontier": len(heap)}]

    while heap and len(visited) < len(graph):
        w, u, v = heapq.heappop(heap)
        if v in visited:                      # would create a cycle: skip
            continue
        visited.add(v)
        mst.append((u, v, w))
        total += w
        for x, wx in graph[v]:
            if x not in visited:
                heapq.heappush(heap, (wx, v, x))
        steps.append(
            {"step": len(steps) + 1, "added": v, "via": (u, v, w), "total": total, "frontier": len(heap)}
        )

    connected = len(visited) == len(graph)
    return mst, total, steps, connected


# --------------------------------------------------------------------------
# 3. Helpers
# --------------------------------------------------------------------------
def total_weight(edges):
    return sum(w for _, _, w in edges)


def edge_key(a, b):
    return tuple(sorted((a, b)))


def is_spanning_tree(nodes, mst_edges):
    """True if the edges connect all nodes with exactly V-1 edges and no cycle."""
    if len(mst_edges) != len(nodes) - 1:
        return False
    uf = UnionFind(nodes)
    for a, b, _ in mst_edges:
        if not uf.union(a, b):
            return False
    return True


def random_connected_graph(n, m, seed=0, max_w=1000):
    """Random connected graph with n nodes and m edges (m >= n-1) - for benchmarking/tests."""
    rng = random.Random(seed)
    nodes = [f"N{i}" for i in range(n)]
    present = set()
    edges = []
    order = nodes[:]
    rng.shuffle(order)
    for i in range(1, n):                                   # random spanning tree first
        a, b = order[i], order[rng.randrange(i)]
        present.add(edge_key(a, b))
        edges.append((a, b, rng.randint(1, max_w)))
    max_edges = n * (n - 1) // 2
    m = min(m, max_edges)
    while len(edges) < m:
        a, b = rng.sample(nodes, 2)
        k = edge_key(a, b)
        if k not in present:
            present.add(k)
            edges.append((a, b, rng.randint(1, max_w)))
    return nodes, edges


def benchmark(sizes=(100, 200, 400, 800, 1600), edges_per_node=5, repeats=3):
    """Time Kruskal and Prim on random graphs. Returns a list of dict rows (milliseconds)."""
    rows = []
    for n in sizes:
        nodes, edges = random_connected_graph(n, edges_per_node * n, seed=n)
        graph = build_graph(nodes, edges)
        best_k = best_p = float("inf")
        for _ in range(repeats):
            t = time.perf_counter()
            _, tk, _, _ = kruskal(nodes, edges)
            best_k = min(best_k, time.perf_counter() - t)
            t = time.perf_counter()
            _, tp, _, _ = prim(graph, nodes[0])
            best_p = min(best_p, time.perf_counter() - t)
        assert tk == tp, "Kruskal and Prim must give the same total weight"
        rows.append(
            {"Nodes (V)": n, "Edges (E)": len(edges), "Kruskal (ms)": round(best_k * 1000, 2),
             "Prim (ms)": round(best_p * 1000, 2), "MST total": tk}
        )
    return rows
