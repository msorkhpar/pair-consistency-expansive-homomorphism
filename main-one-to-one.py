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
    G = construct_nxgraph(config.g_graph_path, type=nx.DiGraph)
    H = construct_nxgraph(config.h_graph_path, type=nx.DiGraph, add_self_loops=True)
    undirected_H = construct_nxgraph(config.h_graph_path)

    # calculate_self_loop_cost(G, H, costs, gamma)
    h_edge_pairs = [NodePair((i, j), length) for (i, j), length in build_degree_two_paths(undirected_H).items()]

    g_to_h_costs: dict[EdgeMap, dict[str, float]] = calculate_mapping_cost(G, H, h_edge_pairs, alpha, beta)
    solver = Solver(G, H, h_edge_pairs, g_to_h_costs)
    solution = solver.solve()
    logger.info(f"G to H mapping cost: {solution.cost}")

    winner_costs = {}
    for key in solution.variables.keys():
        u, v, i, j = key.e1.v1, key.e1.v2, key.e2.v1, key.e2.v2
        dual_key = EdgeMap(NodePair((v, u)), NodePair((j, i)))
        if winner_costs.get(dual_key) is None:
            winner_costs[key] = g_to_h_costs[key]
    draw_LP_result(G, H, None, winner_costs)

    mapper_graph = nx.Graph()
    mapped_subgraph = nx.Graph()
    for key in winner_costs.keys():
        u, v, i, j = key.e1.v1, key.e1.v2, key.e2.v1, key.e2.v2
        mapper_graph.add_edge(u, v)
        mapped_subgraph.add_edge(i, j)
    similarity = similarity_check.eigenvector_similarity.similarity(mapper_graph, mapped_subgraph)
    print(similarity)
