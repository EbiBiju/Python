"""Map drawing for the Network Optimization prototype (shared by the app and the report)."""

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt

from graph_data import EDGES, POSITIONS
from mst import edge_key

# where each place name sits relative to its dot (keeps labels from overlapping)
LABEL_POS = {
    "Majestic": "left", "Cubbon Park": "above", "MG Road": "below",
    "Ulsoor Lake": "above", "Indiranagar": "right", "Domlur": "right",
    "Koramangala": "right", "CHRIST University": "above", "Lalbagh": "right",
    "Jayanagar": "left", "Basavanagudi": "left", "Banashankari": "below",
    "JP Nagar": "below", "BTM Layout": "above", "Silk Board": "below",
    "HSR Layout": "right", "Bellandur": "below", "Marathahalli": "below",
    "Whitefield": "below", "KR Puram": "above", "Electronic City": "below",
    "Hebbal": "above", "Yeshwanthpur": "left", "Rajajinagar": "left",
    "Malleshwaram": "right",
}
OFFSETS = {  # (x, y) offset in points, horizontal align, vertical align
    "below": ((0, -9), "center", "top"),
    "above": ((0, 9), "center", "bottom"),
    "left": ((-9, 0), "right", "center"),
    "right": ((9, 0), "left", "center"),
}
OUTLINE = [pe.withStroke(linewidth=3, foreground="white")]


def km(metres):
    return f"{metres / 1000:.1f}"


def draw_network(mst_edges, show_candidates=True, start=None, figsize=(9, 8.6), label_links=True):
    """
    Draw all candidate links in light grey and the chosen MST links in bold colour.
    mst_edges : list of (a, b, w). start : optional node to mark (Prim's start).
    """
    fig, ax = plt.subplots(figsize=figsize)
    chosen = {edge_key(a, b) for a, b, _ in mst_edges}

    if show_candidates:
        for a, b, _ in EDGES:
            if edge_key(a, b) in chosen:
                continue
            (x1, y1), (x2, y2) = POSITIONS[a], POSITIONS[b]
            ax.plot([x1, x2], [y1, y2], color="#D5D9E0", lw=0.8, zorder=1)

    for a, b, w in mst_edges:
        (x1, y1), (x2, y2) = POSITIONS[a], POSITIONS[b]
        ax.plot([x1, x2], [y1, y2], color="#E4572E", lw=3.2, zorder=3, solid_capstyle="round")
        if label_links:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2, km(w), fontsize=7.5, fontweight="bold",
                    color="#B23A18", ha="center", va="center", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="#E4572E", lw=0.7))

    for n, (x, y) in POSITIONS.items():
        color = "#2E9E5B" if n == start else "#3B6EA8"
        ax.scatter(x, y, s=150, color=color, zorder=4, edgecolors="white", linewidths=1.8)
        (dx, dy), ha, va = OFFSETS[LABEL_POS.get(n, "below")]
        ax.annotate(n, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va=va,
                    fontsize=8.5, color="#111827", zorder=5, path_effects=OUTLINE)

    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.margins(0.12)
    fig.tight_layout()
    return fig
