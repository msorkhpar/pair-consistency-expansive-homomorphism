import logging

import networkx as nx

import similarity_check.eigenvector_similarity
from cost_function.self_loop_cost import calculate_self_loop_cost
from lp.parameters import NodePair, EdgeMap
from lp.solver import Solver
from utils.config import Config
from utils.h_path_builder import build_degree_two_paths
from utils.nxgraph_reader import construct_nxgraph
from utils.result_drawer import draw_LP_result
from cost_function.mapping_cost import calculate_mapping_cost


def __compare(dg, d_l_h, u_h):
    h_edge_pairs = [NodePair((i, j), data["length"], data["path"]) for (i, j), data in
                    build_degree_two_paths(u_h).items()]

    g_to_h_costs: dict[EdgeMap, dict[str, float]] = calculate_mapping_cost(dg, d_l_h, h_edge_pairs, alpha, beta)
    solver_g_to_h_solver = Solver(dg, d_l_h, h_edge_pairs, g_to_h_costs)
    g_to_h = solver_g_to_h_solver.solve()
    logger.info(g_to_h)
    solver_g_to_h_solver.clear()

    mapping_costs = {}
    for key in g_to_h.variables.keys():
        u, v, i, j = key.e1.v1, key.e1.v2, key.e2.v1, key.e2.v2
        dual_key = EdgeMap(NodePair((v, u)), NodePair((j, i)))
        if mapping_costs.get(dual_key) is None:
            mapping_costs[key] = g_to_h_costs[key]
    return mapping_costs, g_to_h.cost


if __name__ == '__main__':
    alpha = 0.7  # distance
    beta = 0.3  # length

    config = Config()
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=config.log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Loaded configurations:{config}")
    logger.info(f"{config.g_graph_path} to {config.h_graph_path}")
    directed_g = construct_nxgraph(config.g_graph_path, type=nx.DiGraph)
    directed_loop_h = construct_nxgraph(config.h_graph_path, type=nx.DiGraph, add_self_loops=True)
    undirected_h = construct_nxgraph(config.h_graph_path)

    g_to_h_mappings, g_to_h_cost = __compare(directed_g, directed_loop_h, undirected_h)
    draw_LP_result(directed_g, undirected_h, None, g_to_h_mappings)
