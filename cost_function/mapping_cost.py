import math

import networkx as nx

from cost_function.length_cost import length_cost
from cost_function.angle_cost import angle_cost
from cost_function.distance_cost import distance_cost
from cost_function.direction_cost import direction_cost
from cost_function.orientation_cost import orientation_cost
from lp.parameters import NodePair, EdgeMap
from utils.max_pair_distance_calculator import calculate_max_pair_distance


def _total_length(graph: nx.Graph):
    total_length = 0
    min_length = math.inf
    for u, v in graph.edges():
        weight = math.dist(u, v)
        total_length += weight
        if min_length > weight and weight > 0:
            min_length = weight
    return total_length, min_length


def _calculate_uv_ij_cost(max_distance, total_G_length, min_g_length, total_H_length, min_h_length, alpha, beta, uv,
                          uv_length, ij, ij_length):
    distance = round(distance_cost(alpha, max_distance, uv.v1, uv.v2, ij.v1, ij.v2), 5)
    length = round(
        length_cost(
            beta, total_G_length, total_H_length, min_h_length, uv_length, ij_length, uv.v1, uv.v2, ij.v1, ij.v2), 5
    )

    return {
        "cost": round((length + distance), 6),
        "length": length,
        "distance": distance,
    }


def calculate_mapping_cost(G: nx.Graph, H: nx.Graph, H_edge_pairs: list[NodePair], alpha, beta) -> dict[
    EdgeMap, dict[str, float]]:
    result: dict[[EdgeMap, dict[str, float]]] = dict()
    max_distance = calculate_max_pair_distance(G, H)
    total_g_length, min_g_length = _total_length(G)
    total_h_length, min_h_length = _total_length(H)

    for uv in [NodePair(e) for e in G.edges()]:
        uv_length = math.dist(uv.v1, uv.v2)
        for ij in H_edge_pairs:
            result.update(
                {
                    EdgeMap(uv, ij):
                        _calculate_uv_ij_cost(
                            max_distance, total_g_length, min_g_length, total_h_length, min_h_length, alpha, beta, uv,
                            uv_length, ij, ij.length
                        )
                }
            )
    return result
