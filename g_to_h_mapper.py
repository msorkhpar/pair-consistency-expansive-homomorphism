import logging

import networkx as nx

from cost_function.mapping_cost import calculate_mapping_cost
from lp.parameters import NodePair, EdgeMap
from lp.solver import Solver
from utils.h_path_builder import build_degree_two_paths

logger = logging.getLogger(__name__)


def __graph_to_image(u_h, mappings, use_paths) -> tuple[nx.Graph, float]:
    h_edge_pairs = {(i, j): NodePair((i, j), data["length"], data["path"]) for (i, j), data in
                    build_degree_two_paths(u_h, use_paths).items()}
    graph_to_image = nx.Graph()
    graph_to_image_edges = 0
    for key in mappings.keys():
        u, v, i, j = key.e1.v1, key.e1.v2, key.e2.v1, key.e2.v2
        path = h_edge_pairs[(i, j)].path
        for n_index in range(len(path) - 1):
            p1 = path[n_index]
            p2 = path[n_index + 1]
            weight = h_edge_pairs[p1, p2].length
            if graph_to_image.has_edge(p1, p2):
                graph_to_image[p1][p2]["weight"] *= 10
            else:
                if p1 != p2:
                    graph_to_image_edges += weight
                graph_to_image.add_edge(p1, p2, weight=weight)

    prime_coverage = graph_to_image_edges / sum(
        data['weight'] for i, j, data in u_h.edges(data=True) if i != j)

    return graph_to_image, prime_coverage


def map_g_to_h(directed_g, directed_loops_h, undirected_h, g_aspect_ratio, h_aspect_ratio, alpha, beta, gamma,
               use_paths):
    h_edge_pairs = {(i, j): NodePair((i, j), data["length"], data["path"]) for (i, j), data in
                    build_degree_two_paths(undirected_h, use_paths).items()}

    g_to_h_costs: dict[EdgeMap, dict[str, float]] = calculate_mapping_cost(directed_g, directed_loops_h,
                                                                           list(h_edge_pairs.values()),
                                                                           alpha, beta, gamma, g_aspect_ratio,
                                                                           h_aspect_ratio)
    solver_g_to_h_solver = Solver(directed_g, directed_loops_h, list(h_edge_pairs.values()), g_to_h_costs)
    g_to_h = solver_g_to_h_solver.solve()
    logger.info(g_to_h)
    solver_g_to_h_solver.clear()

    mappings = {}
    for key in g_to_h.variables.keys():
        u, v, i, j = key.e1.v1, key.e1.v2, key.e2.v1, key.e2.v2
        dual_key = EdgeMap(NodePair((v, u)), NodePair((j, i)))
        if mappings.get(dual_key) is None:
            mappings[key] = g_to_h_costs[key]
    h_prime, h_prime_coverage = __graph_to_image(undirected_h, mappings, use_paths=use_paths)
    return mappings, g_to_h.cost, h_prime, h_prime_coverage
