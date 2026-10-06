"""
Map data for the Network Optimization prototype: a fibre-optic network
connecting 25 hubs in Bengaluru.

LANDMARKS : real Bengaluru localities with approximate GPS coordinates.

CANDIDATE LINKS : every pair of hubs that are within MAX_LINK_KM of each other
    (straight-line) is a possible cable route. This is an ASSUMPTION made for
    the demo - they are not real fibre routes. 8 km is the smallest round
    number that keeps the whole network connected (Electronic City is far from
    everything else, so it only gets one possible link).

CABLE LENGTH (the edge weight) = straight-line (haversine) distance x CIRCUITY.
    Cables are laid along roads, which are on average ~30% longer than a
    straight line, hence 1.3. Rounded to the nearest 100 m so all arithmetic is
    exact integer metres. These are estimates, not surveyed lengths. To use
    real figures, add them to WEIGHT_OVERRIDES.
"""

import itertools
import math

from mst import build_graph

CIRCUITY = 1.3
MAX_LINK_KM = 8.0

# name: (latitude, longitude) - approximate
LANDMARKS = {
    "Majestic": (12.9770, 77.5713),
    "Cubbon Park": (12.9763, 77.5929),
    "MG Road": (12.9756, 77.6065),
    "Ulsoor Lake": (12.9831, 77.6196),
    "Indiranagar": (12.9784, 77.6408),
    "Domlur": (12.9610, 77.6387),
    "Koramangala": (12.9352, 77.6245),
    "CHRIST University": (12.9346, 77.6063),
    "Lalbagh": (12.9507, 77.5848),
    "Jayanagar": (12.9308, 77.5838),
    "Basavanagudi": (12.9422, 77.5737),
    "Banashankari": (12.9255, 77.5468),
    "JP Nagar": (12.9063, 77.5857),
    "BTM Layout": (12.9166, 77.6101),
    "Silk Board": (12.9177, 77.6228),
    "HSR Layout": (12.9116, 77.6474),
    "Bellandur": (12.9304, 77.6784),
    "Marathahalli": (12.9569, 77.7011),
    "Whitefield": (12.9698, 77.7500),
    "KR Puram": (13.0035, 77.6960),
    "Electronic City": (12.8452, 77.6602),
    "Hebbal": (13.0358, 77.5970),
    "Yeshwanthpur": (13.0285, 77.5400),
    "Rajajinagar": (12.9916, 77.5550),
    "Malleshwaram": (13.0035, 77.5710),
}

# Optional exact measured cable lengths in metres: {("Majestic", "Cubbon Park"): 3200}
WEIGHT_OVERRIDES = {}


def haversine_m(a, b):
    """Great-circle (straight-line) distance in metres between two (lat, lon) points."""
    r = 6371000.0
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(h))


def _weight(a, b):
    if (a, b) in WEIGHT_OVERRIDES:
        return WEIGHT_OVERRIDES[(a, b)]
    if (b, a) in WEIGHT_OVERRIDES:
        return WEIGHT_OVERRIDES[(b, a)]
    est = haversine_m(LANDMARKS[a], LANDMARKS[b]) * CIRCUITY
    return int(round(est / 100.0)) * 100


NODES = list(LANDMARKS.keys())
EDGES = [
    (a, b, _weight(a, b))
    for a, b in itertools.combinations(NODES, 2)
    if haversine_m(LANDMARKS[a], LANDMARKS[b]) <= MAX_LINK_KM * 1000
]

# (x, y) for drawing: longitude scaled by cos(latitude) so the map is not stretched
_LAT0 = sum(lat for lat, _ in LANDMARKS.values()) / len(LANDMARKS)
POSITIONS = {
    name: (lon * math.cos(math.radians(_LAT0)), lat) for name, (lat, lon) in LANDMARKS.items()
}


def load_graph():
    return build_graph(NODES, EDGES)
