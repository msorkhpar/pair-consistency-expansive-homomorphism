import math
import networkx as nx


def calculate_max_pair_distance(G: nx.Graph, H: nx.Graph):
    max_distance = 0
    H_edge_pairs = list(H.edges()) + [(v, u) for u, v in H.edges()]
    for u, v in G.edges():
        for i, j in H_edge_pairs:
            distance = math.dist(u, i) + math.dist(v, j)
            if distance > max_distance:
                max_distance = distance + 1
    return max_distance
