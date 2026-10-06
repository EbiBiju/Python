# Bengaluru Network Optimizer: Kruskal's and Prim's Algorithms

**Course:** Design and Analysis of Algorithms (DAA) · **Assessment:** CIA3 Prototype Development
**Topic:** Network Optimization (Minimum Spanning Tree)

A small working prototype that connects 25 Bengaluru hubs (a fibre-optic network) with the
**least total cable**. It implements **Kruskal's** and **Prim's** algorithms from scratch, shows
every step of both, draws the optimised network on a map of the city, and checks that they agree.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py          # opens the web app in your browser
python test_mst.py            # correctness tests (optional)
```

On Windows, if `pip` is not recognised, use `python -m pip install -r requirements.txt` and
`python -m streamlit run app.py`.

## Files

| File | Purpose |
|---|---|
| `mst.py` | The algorithms: Union-Find, Kruskal, Prim (heap), benchmark helpers |
| `graph_data.py` | The Bengaluru data: 25 hubs (GPS coordinates), candidate links, cable-length estimates |
| `plotting.py` | Draws the network on a map |
| `app.py` | Streamlit interface: choose algorithm, map, step-by-step tables, comparison, benchmark |
| `test_mst.py` | Checks both algorithms against networkx on the real network and 300 random graphs |
| `sample_output.png`, `sample_app_screenshot.png` | Example output of the app |

## Problem statement

Given a set of locations and the possible cable links between them (each with a length), choose
the links so that **every location is connected** and the **total cable length is minimum**.
This is the Minimum Spanning Tree (MST) problem: V − 1 links, no loops.

## About the data (be ready to explain this)

- **Hubs:** 25 real Bengaluru localities at approximate GPS coordinates (Majestic, MG Road, Koramangala, CHRIST University, Whitefield, Electronic City, ...).
- **Candidate links:** every pair of hubs within 8 km (straight-line) is treated as a possible cable route, giving 142 candidates. **This is an assumption for the demo, not a real fibre map.** 8 km is the smallest round value that keeps the network connected; Electronic City is far from everything, so it only gets one possible link (to HSR Layout), which must therefore be in the MST.
- **Cable length:** straight-line (haversine) distance × 1.3 (cables follow roads, which are roughly 30% longer than a straight line), rounded to the nearest 100 m. These are estimates, not surveyed lengths. Real figures can be added in `WEIGHT_OVERRIDES` in `graph_data.py`.
- **Saving figure:** "cable saved" compares the MST with building **every** candidate link (949.8 km). That is a deliberately wasteful baseline, used only to show the scale of the saving.

## How the algorithms work

**Kruskal (greedy on edges)**
1. Sort all links by length.
2. Take the next shortest link. If it joins two hubs that are not yet connected, accept it; otherwise it would form a loop, so reject it (loop check = Union-Find).
3. Stop when V − 1 links are accepted.

**Prim (greedy on vertices)**
1. Start the tree at any hub and put its links in a min-heap.
2. Repeatedly remove the cheapest link. If it reaches a new hub, add that hub and the link, and push the new hub's links into the heap. If the hub is already in the tree, skip it.
3. Stop when all hubs are in the tree.

**Why greedy is correct (cut property):** for any split of the hubs into two groups, the cheapest link crossing the split belongs to some MST. Both algorithms only ever add such a link.

## Complexity

| | Kruskal | Prim (binary heap) |
|---|---|---|
| Time | O(E log E) = O(E log V) | O((V + E) log V) |
| Space | O(V + E) | O(V + E) |
| Main data structure | Union-Find (path compression + union by rank) | Binary min-heap |
| Works well on | Sparse graphs | Dense graphs (with a better heap) |

V = 25 hubs, E = 142 candidate links. Union-Find operations cost O(α(V)) amortised, which is practically constant.

## Results on the Bengaluru network

- Minimum cable: **93.8 km** using **24 links** (vs 949.8 km if all 142 candidates were built).
- Kruskal examined 133 of the 142 links and rejected 109 as loops.
- Prim gives the same total from every possible starting hub and the same set of links.
- Longest chosen link: HSR Layout – Electronic City (9.8 km), the only possible link for Electronic City.

## Limitations

- Link lengths are estimates and the candidate links are an assumption.
- A tree has **no backup path**: if one link fails, the network splits in two. Real networks add extra links (a ring) for redundancy.
- Weights are lengths only; real cost also depends on terrain, permits and capacity.
- Both algorithms need non-negative weights here (cable lengths); the code rejects negative ones.

## Likely viva questions

- **What is a spanning tree / MST?** A set of V − 1 links that connects all V nodes with no loop; the MST is the one with the smallest total weight.
- **Kruskal vs Prim?** Kruskal sorts edges and merges groups (edge-centric); Prim grows one tree from a start node (vertex-centric). Both give the same total weight.
- **Why Union-Find in Kruskal?** To check in near-constant time whether a link would create a loop, instead of searching the graph each time.
- **Why does Prim use a heap?** To pick the cheapest link out of the frontier in O(log E) rather than scanning all links.
- **Is the MST unique?** The total weight is; the set of links is only unique if all weights are distinct. The tests use graphs with many tied weights to check this.
- **Which is faster?** Depends on density: Kruskal's O(E log V) is fine for sparse graphs; Prim with a heap is similar, and better with a Fibonacci heap on dense graphs. The benchmark in the app shows both are close on random graphs.
- **What if the graph is disconnected?** No spanning tree exists. Kruskal returns a spanning forest and Prim only reaches the start's component; the code reports `connected = False`.
- **Real-world uses:** laying cable/pipelines/roads, network design, clustering.

## Customising

Edit `LANDMARKS` (name → latitude, longitude) and `MAX_LINK_KM` in `graph_data.py`. For a new place, add a label position in `LABEL_POS` in `plotting.py` (optional; it defaults to below the dot).
