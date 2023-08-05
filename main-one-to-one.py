import logging

import networkx as nx

from g_to_h_mapper import map_g_to_h
from utils.assign_weight_to_edges import assign_edge_weights
from utils.config import Config
from utils.graph_frame_finder import find_aspect_ratio
from utils.nxgraph_reader import construct_nxgraph
from utils.result_drawer import draw_LP_result

logger = logging.getLogger(__name__)

alpha = 2
beta = 3
gamma = 9

use_path_g_to_h = True
use_path_h_to_g = True

if __name__ == '__main__':
    config = Config()
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=config.log_level)

    logger.info(f"Loaded configurations:{config}")
    logger.info(f"{config.g_graph_path} to {config.h_graph_path}")
    directed_g = construct_nxgraph(config.g_graph_path, type=nx.DiGraph)
    g_aspect_ratio = find_aspect_ratio(directed_g)

    directed_loop_h = construct_nxgraph(config.h_graph_path, type=nx.DiGraph, add_self_loops=True)
    undirected_h = construct_nxgraph(config.h_graph_path)
    assign_edge_weights(undirected_h)
    h_aspect_ratio = find_aspect_ratio(undirected_h)

    g_to_h_mappings, g_to_h_cost, h_prime, h_prime_coverage = map_g_to_h(directed_g, directed_loop_h,
                                                                         undirected_h, g_aspect_ratio,
                                                                         h_aspect_ratio, alpha, beta, gamma,
                                                                         use_path_g_to_h)
    draw_LP_result(directed_g, undirected_h, None, g_to_h_mappings, H_prime=h_prime)
