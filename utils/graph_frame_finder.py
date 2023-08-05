import math

import networkx as nx
import numpy as np

from utils.config import Config


def find_aspect_ratio(graph: nx.Graph):
    x1, y1 = np.inf, np.inf
    x2, y2 = -np.inf, -np.inf
    for x, y in graph.nodes:
        x1 = min(x1, x)
        y1 = min(y1, y)
        x2 = max(x2, x)
        y2 = max(y2, y)
    width = x2 - x1
    height = y2 - y1

    if math.isinf(width) or width <= 1:
        return 1
    if math.isinf(height) or height <= 1:
        return 1

    return min(width, height) / max(width, height)
