import csv
import logging

import os
from functools import cmp_to_key
from operator import itemgetter
from typing import List, Any
import shutil

from lp.solver import Solver
from utils.config import Config
from utils.nxgraph_reader import construct_nxgraph
from utils.result_drawer import draw_LP_result


if __name__ == '__main__':
    config = Config()
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=config.log_level)
    logger = logging.getLogger(__name__)
    logger.info(f"Loaded configurations:{config}")

    G = construct_nxgraph(config.g_graph_path)

    result = []
    counter = 0
    for root, directories, h_adjlists in os.walk(config.computerized_graphs_dir):
        for h_adjlist in h_adjlists:
            counter += 1
            h_adjlist_path = os.path.join(root, h_adjlist)
            h_name = h_adjlist.split(".")[0]
            H = construct_nxgraph(h_adjlist_path)
            if H.number_of_nodes() < 2:
                continue
            logger.info(f"Running against {h_name}")
            solver_g_to_h_solver = Solver(G, H)
            g_to_h = solver_g_to_h_solver.solve()
            solver_g_to_h_solver.clear()
            logger.info(g_to_h)
            if not g_to_h:
                continue

            first_distance = 0 if g_to_h is None else g_to_h.distance
            first_time = 0 if g_to_h is None else g_to_h.running_time
            result.append([
                h_name,
                first_distance,
                first_time,
            ])
            logger.info(f"Solved so far: {counter}")

    result.sort(key=lambda x: x[1])
    final = list()
    for i in range(len(result) // 1):
        row = result[i]
        h_name = row[0]
        first_distance = row[1]
        first_time = row[2]
        h_adjlist_path = os.path.join(config.computerized_graphs_dir, f"{h_name}.adjlist")
        H = construct_nxgraph(h_adjlist_path)

        solver_g_to_h_solver = Solver(G, H)
        g_to_h = solver_g_to_h_solver.solve()
        solver_g_to_h_solver.clear()

        g_to_h_values = list(g_to_h.variables.keys())

        solver_h_to_g_solver = Solver(H, G)
        h_to_g = solver_h_to_g_solver.solve()
        solver_h_to_g_solver.clear()

        if not h_to_g:
            continue
        h_to_g_values = list(h_to_g.variables.keys())

        logger.info(h_to_g)
        second_distance = 0 if h_to_g is None else h_to_g.distance
        delta_distance = abs(second_distance - first_distance)
        second_time = 0 if h_to_g is None else h_to_g.running_time
        final.append([
            h_name,
            delta_distance,
            first_distance,
            second_distance,
            first_time,
            second_time
        ])
        draw_LP_result(G, H, os.path.join(output_path, f"{h_name}.png"), g_to_h_values, h_to_g_values)

    final = sorted(final, key=cmp_to_key(sorting))
    with open(os.path.join(output_path, "result.csv"), 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["name", "delta distance", "G to H distance", "H to G distance", "G->H time", "H->G time"])
        writer.writerows(final)
