import math

import networkx as nx

from cost_function.length_cost import length_cost
from cost_function.angle_cost import angle_cost
from cost_function.distance_cost import distance_cost
from cost_function.direction_cost import direction_cost
from cost_function.orientation_cost import orientation_cost
from lp.parameters import Edge, EdgeMap
from utils.max_pair_distance_calculator import calculate_max_pair_distance


def _total_length(G: nx.Graph):
    total_length = 0
    for u, v in G.edges():
        total_length += math.dist(u, v)
    return total_length


def calculate_mapping_cost(G: nx.Graph, H: nx.Graph, alpha, beta, gamma, delta, tau) -> dict[EdgeMap, dict[str, float]]:
    result: dict[[EdgeMap, dict[str, float]]] = dict()
    max_distance = calculate_max_pair_distance(G, H)
    total_G_length = _total_length(G)
    total_H_length = _total_length(H)
    H_edge_pairs = list(H.edges()) + [(v, u) for u, v in H.edges()]

    for uv in [Edge(e) for e in G.edges]:
        for ij in [Edge(e2) for e2 in H_edge_pairs]:
            length = round(length_cost(alpha, total_G_length, total_H_length, uv.v1, uv.v2, ij.v1, ij.v2), 1)
            angle = round(angle_cost(beta, uv.v1, uv.v2, ij.v1, ij.v2), 1)
            distance = round(distance_cost(gamma, max_distance, uv.v1, uv.v2, ij.v1, ij.v2), 1)
            direction = round(direction_cost(delta, uv.v1, uv.v2, ij.v1, ij.v2), 1)
            orientation = round(orientation_cost(tau, uv.v1, uv.v2, ij.v1, ij.v2), 1)
            result.update({
                EdgeMap(uv, ij): {
                    "cost": round(length * angle * distance * direction * orientation, 3),
                    "length": length,
                    "angle": angle,
                    "distance": distance,
                    "direction": direction,
                    "orientation": orientation,
                }
            })
    return result
