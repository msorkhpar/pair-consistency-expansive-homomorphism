import networkx as nx

from cost_function.distance_cost import distance_cost
from lp.parameters import EdgeMap, Edge
from utils.max_pair_distance_calculator import calculate_max_pair_distance


def calculate_self_loop_cost(G: nx.Graph, H: nx.Graph, mapping_cost: dict[EdgeMap, dict[str, float]], gamma):
    max_distance = calculate_max_pair_distance(G, H)
    for uv in [Edge(e) for e in G.edges]:
        for i in H.nodes():
            # Find Si where i and its neighbor has orientation 1
            candidates = {}
            candidate = None
            # calculate distance between uv and ii
            uv_ii_distance = distance_cost(gamma, max_distance, uv.v1, uv.v2, i, i)
            for j in H.neighbors(i):
                uv_ij = EdgeMap(uv, Edge((i, j)))
                if mapping_cost[uv_ij]["orientation"] == 1:
                    candidates[uv_ij] = mapping_cost[uv_ij]['cost'] - mapping_cost[uv_ij]['distance'] + uv_ii_distance

            if candidates:
                # Find maximum cost in S and assign it to be the candidate
                candidate = mapping_cost[max(candidates, key=lambda k: candidates[k])]
            else:
                # Find a list where i and its neighbor has orientation 0
                for j in H.neighbors(i):
                    uv_ij = EdgeMap(uv, Edge((i, j)))
                    if mapping_cost[uv_ij]["orientation"] != 1:
                        candidates[uv_ij] = mapping_cost[uv_ij]['cost'] - mapping_cost[uv_ij][
                            'distance'] + uv_ii_distance
                candidate = mapping_cost[min(candidates, key=lambda k: candidates[k])]

            if candidate:
                mapping_cost[EdgeMap(uv, Edge((i, i)))] = {
                    "cost": candidate["cost"] - candidate["distance"] + uv_ii_distance,
                    "length": candidate["length"],
                    "angle": candidate["angle"],
                    "distance": uv_ii_distance,
                    "direction": candidate["direction"],
                    "orientation": candidate["orientation"],
                }