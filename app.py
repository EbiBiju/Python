"""
Bengaluru Network Optimization - DAA CIA3 prototype
Algorithms: Kruskal's and Prim's Minimum Spanning Tree (both written from scratch in mst.py)

Run with:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

from graph_data import CIRCUITY, EDGES, MAX_LINK_KM, NODES, load_graph
from mst import benchmark, edge_key, kruskal, prim, total_weight
from plotting import draw_network, km

st.set_page_config(page_title="Bengaluru Network Optimizer", page_icon="🌐", layout="wide")

graph = load_graph()
places = sorted(NODES)
all_links_total = total_weight(EDGES)

# ------------------------------------------------------------------ header
st.title("🌐 Bengaluru Network Optimizer")
st.caption(
    "Connect 25 Bengaluru hubs with the **least total cable** using **Kruskal's** and **Prim's** "
    "Minimum Spanning Tree algorithms (written from scratch) · Design and Analysis of Algorithms"
)

# ----------------------------------------------------------------- controls
c1, c2 = st.columns([2, 2])
algo = c1.radio("Algorithm", ["Kruskal", "Prim", "Compare both"], horizontal=True)
start = c2.selectbox(
    "Prim's starting hub", places, index=places.index("Majestic"),
    help="Prim grows the network outwards from this hub. The total length does not depend on it.",
    disabled=(algo == "Kruskal"),
)

# ------------------------------------------------------------------ compute
k_edges, k_total, k_steps, k_conn = kruskal(NODES, EDGES)
p_edges, p_total, p_steps, p_conn = prim(graph, start)

if algo == "Prim":
    shown_edges, shown_total, shown_start = p_edges, p_total, start
else:
    shown_edges, shown_total, shown_start = k_edges, k_total, (start if algo == "Compare both" else None)

if not (k_conn and p_conn):
    st.error("The hubs cannot all be connected with the given candidate links.")
    st.stop()

saving = 100 * (1 - shown_total / all_links_total)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Cable needed (MST)", f"{km(shown_total)} km")
m2.metric("Links built", f"{len(shown_edges)} of {len(EDGES)}")
m3.metric("If every link were built", f"{km(all_links_total)} km")
m4.metric("Cable saved", f"{saving:.1f} %")

# ----------------------------------------------------------- map + steps
left, right = st.columns([1, 1])

with left:
    st.subheader("Optimised network")
    show_candidates = st.checkbox("Show all candidate links (grey)", value=False)
    st.pyplot(draw_network(shown_edges, show_candidates=show_candidates, start=shown_start))
    st.caption(
        "Orange = links chosen for the minimum network (labels = cable length in km) · tick the box to see the other "
        f"possible links in grey (hubs within {MAX_LINK_KM:g} km) · estimated lengths = straight-line × {CIRCUITY}. North is up."
    )

with right:
    if algo in ("Kruskal", "Compare both"):
        st.subheader("Kruskal, step by step")
        st.caption(
            "Edges are sorted by length. Each is accepted only if it joins two separate groups; "
            "otherwise it would form a loop and is rejected (found with Union-Find)."
        )
        rows = [
            {
                "Step": s["step"],
                "Link": f"{s['edge'][0]} – {s['edge'][1]}",
                "Km": km(s["edge"][2]),
                "Decision": s["decision"],
                "Total km": km(s["total"]),
                "Groups": s["components"],
            }
            for s in k_steps
        ]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=300 if algo == "Compare both" else 520)
    if algo in ("Prim", "Compare both"):
        st.subheader(f"Prim from {start}, step by step")
        st.caption(
            "The network grows from one hub. Each step adds the cheapest link that reaches a hub "
            "not yet connected (cheapest found with a min-heap)."
        )
        rows = [
            {
                "Step": s["step"],
                "Hub added": s["added"],
                "Via link": "start" if s["via"] is None else f"{s['via'][0]} – {s['via'][1]}",
                "Km": "—" if s["via"] is None else km(s["via"][2]),
                "Total km": km(s["total"]),
                "Heap": s["frontier"],
            }
            for s in p_steps
        ]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=300 if algo == "Compare both" else 520)

# ------------------------------------------------------- Kruskal vs Prim
st.subheader("Kruskal vs Prim on this network")
same_edges = {edge_key(a, b) for a, b, _ in k_edges} == {edge_key(a, b) for a, b, _ in p_edges}
cA, cB = st.columns(2)
cA.metric("Kruskal total", f"{km(k_total)} km")
cA.caption(f"{len(k_steps)} links examined, {sum(s['decision'] != 'accepted' for s in k_steps)} rejected as loops")
cB.metric(f"Prim total (from {start})", f"{km(p_total)} km")
cB.caption(f"{len(p_steps) - 1} links added, one per new hub")
if k_total == p_total:
    st.success(
        "Both algorithms give the same minimum total length"
        + (" and the same set of links." if same_edges else
           ", but chose a different set of links (possible when two links have equal length, "
           "since an MST is then not unique).")
    )
else:  # should never happen
    st.error("Totals differ: this indicates a bug.")

with st.expander("Speed comparison on random graphs (click to run)"):
    st.caption("Random connected graphs with 5 edges per node. Times depend on your computer.")
    if st.button("Run benchmark"):
        with st.spinner("Timing both algorithms..."):
            st.session_state["bench"] = pd.DataFrame(benchmark())
    if "bench" in st.session_state:
        bench = st.session_state["bench"]
        st.dataframe(bench, hide_index=True, width="stretch")
        st.line_chart(bench.set_index("Nodes (V)")[["Kruskal (ms)", "Prim (ms)"]])

with st.expander("Algorithm & complexity"):
    st.markdown(
        f"""
- **Goal:** connect all V hubs with the minimum total cable. The answer is a *minimum spanning tree*: V − 1 links, no loops.
- **Kruskal (greedy on edges):** sort all links by length, then add the shortest one that does not create a loop. Loop check = Union-Find (path compression + union by rank).
  Time **O(E log E) = O(E log V)** · Space O(V + E).
- **Prim (greedy on vertices):** start at one hub and repeatedly add the cheapest link that reaches a new hub, using a binary min-heap.
  Time **O((V + E) log V)** · Space O(V + E).
- **Why greedy works (cut property):** for any split of the hubs into two groups, the cheapest link crossing the split belongs to some MST.
- **This network:** V = {len(NODES)} hubs, E = {len(EDGES)} candidate links.
- **Limitations:** link lengths are estimates (straight-line × {CIRCUITY}); every pair within {MAX_LINK_KM:g} km is assumed to be a possible route; a tree has no backup path if one link fails.
        """
    )
