import math

import networkx as nx
import numpy as np

from utils.config import Config


def graph_width_height_frame(graph: nx.Graph):
    x1, y1 = np.inf, np.inf
    x2, y2 = -np.inf, -np.inf
    for x, y in graph.nodes:
        x1 = min(x1, x)
        y1 = min(y1, y)
        x2 = max(x2, x)
        y2 = max(y2, y)
    width = x2 - x1
    height = y2 - y1

    if math.isinf(width) or width == 0:
        width = 1
    if math.isinf(height) or height == 0:
        height = 1

    return width, height
