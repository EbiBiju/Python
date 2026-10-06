"""
Correctness tests: our from-scratch Kruskal and Prim are checked against networkx
(networkx is used ONLY here, as an independent reference).

Run with:  python test_mst.py
"""

import networkx as nx

from graph_data import EDGES, NODES, load_graph
from mst import (UnionFind, build_graph, is_spanning_tree, kruskal, prim,
                 random_connected_graph, total_weight)


def nx_mst_total(nodes, edges):
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_weighted_edges_from(edges)
    return sum(d["weight"] for _, _, d in nx.minimum_spanning_edges(G, data=True))


def test_bengaluru_network():
    graph = load_graph()
    expected = nx_mst_total(NODES, EDGES)
    k_edges, k_total, _, k_conn = kruskal(NODES, EDGES)
    assert k_conn and k_total == expected and is_spanning_tree(NODES, k_edges)
    for start in NODES:                                   # Prim from every possible start
        p_edges, p_total, _, p_conn = prim(graph, start)
        assert p_conn and p_total == expected, f"Prim from {start}: {p_total} != {expected}"
        assert is_spanning_tree(NODES, p_edges)
    print(f"PASS  Bengaluru network: Kruskal and Prim (from all {len(NODES)} start nodes) "
          f"= networkx = {expected} m")


def test_random_graphs():
    count = 0
    for seed in range(300):
        n = 3 + seed % 40
        m = min(n * (n - 1) // 2, n - 1 + (seed * 7) % (3 * n))
        nodes, edges = random_connected_graph(n, m, seed=seed, max_w=20)   # small weights -> many ties
        graph = build_graph(nodes, edges)
        expected = nx_mst_total(nodes, edges)
        k_edges, k_total, _, _ = kruskal(nodes, edges)
        p_edges, p_total, _, _ = prim(graph, nodes[seed % n])
        assert k_total == p_total == expected, f"seed {seed}: {k_total}, {p_total}, {expected}"
        assert is_spanning_tree(nodes, k_edges) and is_spanning_tree(nodes, p_edges)
        count += 1
    print(f"PASS  {count} random graphs (many with tied weights) match networkx")


def test_all_equal_weights():
    nodes = list("ABCDE")
    edges = [(a, b, 7) for i, a in enumerate(nodes) for b in nodes[i + 1:]]
    assert kruskal(nodes, edges)[1] == 4 * 7
    assert prim(build_graph(nodes, edges), "A")[1] == 4 * 7
    print("PASS  all-equal weights (MST is not unique, total is)")


def test_disconnected_graph():
    nodes = ["A", "B", "C", "D"]
    edges = [("A", "B", 1), ("C", "D", 2)]
    k_edges, k_total, _, k_conn = kruskal(nodes, edges)
    p_edges, p_total, _, p_conn = prim(build_graph(nodes, edges), "A")
    assert not k_conn and k_total == 3 and len(k_edges) == 2     # spanning forest
    assert not p_conn and p_total == 1 and len(p_edges) == 1     # only A's component
    print("PASS  disconnected graph is detected (no spanning tree exists)")


def test_single_node_and_negative():
    assert kruskal(["A"], [])[1] == 0 and prim({"A": []}, "A")[1] == 0
    try:
        kruskal(["A", "B"], [("A", "B", -1)])
    except ValueError:
        print("PASS  single node handled, negative weight rejected")
        return
    raise AssertionError("negative weight should raise ValueError")


def test_union_find():
    uf = UnionFind(["a", "b", "c", "d"])
    assert uf.union("a", "b") and uf.union("c", "d") and uf.union("a", "c")
    assert not uf.union("b", "d")                          # already connected -> cycle
    assert len({uf.find(x) for x in "abcd"}) == 1
    print("PASS  Union-Find detects cycles")


def test_mst_is_cheaper_than_full_network():
    _, total, _, _ = kruskal(NODES, EDGES)
    assert total < total_weight(EDGES)
    print(f"PASS  MST ({total / 1000:.1f} km) is far cheaper than building every link "
          f"({total_weight(EDGES) / 1000:.1f} km)")


if __name__ == "__main__":
    test_bengaluru_network()
    test_random_graphs()
    test_all_equal_weights()
    test_disconnected_graph()
    test_single_node_and_negative()
    test_union_find()
    test_mst_is_cheaper_than_full_network()
    print("\nAll tests passed.")
