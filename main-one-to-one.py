import logging

import networkx as nx
from cost_function.self_loop_cost import calculate_self_loop_cost
from lp.solver import Solver
from utils.config import Config
from utils.nxgraph_reader import construct_nxgraph
from utils.result_drawer import draw_LP_result
from cost_function.mapping_cost import calculate_mapping_cost

if __name__ == '__main__':
    alpha = 1  # length
    beta = 2  # angle
    gamma = 4  # distance
    delta = 1  # direction
    tau = 3  # orientation

    config = Config()
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=config.log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Loaded configurations:{config}")
    logger.info(f"{config.g_graph_path} to {config.h_graph_path}")
    G = construct_nxgraph(config.g_graph_path)
    H = construct_nxgraph(config.h_graph_path, type=nx.DiGraph)

    costs = calculate_mapping_cost(G, H, alpha, beta, gamma, delta, tau)
    calculate_self_loop_cost(G, H, costs, gamma)
    solver = Solver(G, H, costs)
    solution = solver.solve()
    logger.info(f"G to H mapping cost: {solution.cost}")
    winner_costs = {key: costs[key] for key in solution.variables.keys()}

    draw_LP_result(G, H, None, winner_costs)
