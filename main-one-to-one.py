import logging

import os
import shutil

import mapper
from h_prime_builder import HPrime
from input_graph import InputGraph
from result_drawer import MappingDrawer
from solver import Solver
from utils.config import Config

logger = logging.getLogger(__name__)
alpha = 2
beta = 3
gamma = 9

use_path_g_to_h = True
use_path_h_to_g = True


def compare(base_graph: InputGraph, target_graph: InputGraph):
    costs = mapper.MapGtoH(base_graph, target_graph, alpha, beta, gamma).calculate_mapping_costs()
    solution = Solver(base_graph, target_graph, costs).solve()
    target_prime = HPrime(target_graph, solution)
    return costs, solution, target_prime


if __name__ == '__main__':
    config = Config()
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=config.log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Loaded configurations:{config}")
    output_path = "./output"
    shutil.rmtree(output_path, ignore_errors=True)
    os.makedirs(output_path)

    g = InputGraph(config.g_graph_path, use_path_g_to_h)
    h = InputGraph(config.h_graph_path, use_path_h_to_g, "'")
    g_h_costs, g_h_solution, h_prime = compare(g, h)
    h_g_costs, h_g_solution, g_prime = compare(h, g)
    MappingDrawer(os.path.join(output_path, f"1_to_1.png"), g.undirected_graph, h.undirected_graph,
                  h_prime.prime_graph, g_h_solution.variables, g_prime.prime_graph,
                  h_g_solution.variables).draw()
