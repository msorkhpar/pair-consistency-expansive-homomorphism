import csv
import logging
import os
from operator import itemgetter

import networkx as nx
import numpy as np
import cv2

from cost_function.self_loop_cost import calculate_self_loop_cost
from lp.solver import Solver
from utils.config import Config
from utils.nxgraph_reader import construct_nxgraph
from utils.result_drawer import draw_LP_result
from cost_function.mapping_cost import calculate_mapping_cost
from transport.coordinate_transporter import transport_to_cartesian_system

if __name__ == '__main__':
    alpha = 1
    beta = 2
    gamma = 4
    delta = 2
    tau = 2

    config = Config()
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=config.log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Loaded configurations:{config}")
    logger.info(f"{config.g_graph_path} to {config.h_graph_path}")
    G = construct_nxgraph(config.g_graph_path)
    G, G_labels = transport_to_cartesian_system(G, config.input_width, config.input_height)
    H = construct_nxgraph(config.h_graph_path)
    H, H_labels = transport_to_cartesian_system(H, config.input_width, config.input_height)

    costs = calculate_mapping_cost(G, H, alpha, beta, gamma, delta, tau)
    calculate_self_loop_cost(G, H, costs, gamma)

    solver = Solver(G, H, costs)
    solution = solver.solve()
    solution.relabel_variables(G_labels, H_labels)
    logger.info(f"Cost: {solution.cost}")
    for variable, value in solution.variables.items():
        print(f"{variable} = {value}")
    g_h_values = list(solution.variables.keys())
    nx.relabel_nodes(G, G_labels, copy=False)
    nx.relabel_nodes(H, H_labels, copy=False)
    draw_LP_result(G, H, None, g_h_values)
