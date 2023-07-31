import csv
import logging
import networkx as nx
from cost_function.self_loop_cost import calculate_self_loop_cost
from cost_function.mapping_cost import calculate_mapping_cost

import logging

import os
import shutil

from lp.solver import Solver
from utils.config import Config
from utils.nxgraph_reader import construct_nxgraph
from utils.result_drawer import draw_LP_result

if __name__ == '__main__':
    alpha = 1  # length
    beta = 2  # angle
    gamma = 4  # distance
    delta = 1  # direction
    tau = 2  # orientation

    config = Config()
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=config.log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Loaded configurations:{config}")
    output_path = "./output2"
    shutil.rmtree(output_path, ignore_errors=True)
    os.makedirs(output_path)

    G = construct_nxgraph(config.g_graph_path)

    result = []
    counter = 0
    for root, directories, h_adjlists in os.walk(config.computerized_graphs_dir):
        for h_adjlist in h_adjlists:
            counter += 1
            h_adjlist_path = os.path.join(root, h_adjlist)
            h_name = h_adjlist.split(".")[0]
            H = construct_nxgraph(h_adjlist_path, type=nx.DiGraph)
            logger.info(f"Running against {h_name}")

            g_to_h_costs = calculate_mapping_cost(G, H, alpha, beta, gamma, delta, tau)
            calculate_self_loop_cost(G, H, g_to_h_costs, gamma)

            solver_g_to_h_solver = Solver(G, H, g_to_h_costs)
            g_to_h = solver_g_to_h_solver.solve()

            logger.info(g_to_h)
            solver_g_to_h_solver.clear()

            # h_to_g_costs = calculate_mapping_cost(H, G, alpha, beta, gamma, delta, tau)
            # calculate_self_loop_cost(H, G, h_to_g_costs, gamma)
            #
            # solver_h_to_g_solver = Solver(H, G, h_to_g_costs)
            # h_to_g = solver_h_to_g_solver.solve()
            # logger.info(h_to_g)
            #
            # solver_h_to_g_solver.clear()
            winner_costs = {key: g_to_h_costs[key] for key in g_to_h.variables.keys()}
            draw_LP_result(G, H, os.path.join(output_path, f"{h_name}.png"), winner_costs)
            # list(h_to_g.variables.keys()))

            result.append([
                h_name,
                round(g_to_h.cost, 5),
                # round(g_to_h.running_time, 5),
                # round(h_to_g.cost, 5),
                # round(h_to_g.running_time, 5)
            ])

    with open(os.path.join(output_path, "result.csv"), 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["Name of the target file", "G to H cost", ])  # "G->H time"])  # "H to G",  "H->G time"])
        writer.writerows(result)
