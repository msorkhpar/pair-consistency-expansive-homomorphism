import csv

import pandas as pd

import logging

import os
import shutil

from recognition.input_graph import InputGraph
from recognition.lp.solver import Solver
from recognition.mappings import mapper
from recognition.mappings.h_prime_builder import HPrime
from utils.config import Config

logger = logging.getLogger(__name__)
alpha = 2
beta = 3
gamma = 9

use_path_in_g_prime = True
use_path_in_h_prime = True
columns = [f"Target", "Cost_LP(G,H)", "Cost_LP(H,G)", "G' Coverage", "H' Coverage"]


def compare(base_graph: InputGraph, target_graph: InputGraph):
    costs = mapper.MapGtoH(base_graph, target_graph, alpha, beta, gamma).calculate_mapping_costs()
    solution = Solver(base_graph, target_graph, costs).solve()
    target_prime = HPrime(target_graph, solution)
    return costs, solution, target_prime


def pick_top(result):
    df = pd.DataFrame(result, columns=columns)
    g_h_cost = df[df.columns[1]]
    h_g_cost = df[df.columns[2]]
    g_prime_coverage = df[df.columns[3]]
    h_prime_coverage = df[df.columns[4]]

    score = g_h_cost + g_h_cost * (1 - h_prime_coverage) + h_g_cost + h_g_cost * (1 - g_prime_coverage)
    df['Score'] = round(score, 3)
    df.sort_values(by='Score', ascending=True, inplace=True)

    return df.iloc[0][0], df.iloc[0][5]


if __name__ == '__main__':
    config = Config()
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=config.log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Loaded configurations:{config}")

    h_graphs: dict[str, InputGraph] = {}
    output_results = []
    for root, directories, h_adjlists in os.walk(config.computerized_graphs_dir):
        for h_adjlist in h_adjlists:
            h_adjlist_path = os.path.join(root, h_adjlist)
            h_name = h_adjlist.split(".")[0]
            h = InputGraph(h_adjlist_path, use_path_in_h_prime, "'")
            h_graphs[h_name] = h

    statr_time = os.times()[0]
    for root, directories, g_adjlists in os.walk(config.mnist_graphs_dir):
        for g_adjlist in g_adjlists:
            logger.info(f"Checking {g_adjlist}...")
            g_adjlist_path = os.path.join(root, g_adjlist)
            g_name = g_adjlist.split(".")[0]
            g_label = g_name.split("_")[0]
            g = InputGraph(g_adjlist_path, use_path_in_g_prime)
            result = []
            for h_name, h in h_graphs.items():
                g_h_costs, g_h_solution, h_prime = compare(g, h)
                logger.debug(g_h_solution)
                h_g_costs, h_g_solution, g_prime = compare(h, g)
                logger.debug(h_g_solution)

                result.append([
                    h_name, g_h_solution.cost, h_g_solution.cost, g_prime.coverage, h_prime.coverage
                ])

            top_name, score = pick_top(result)
            correct = True if top_name[0] == g_label else False
            output_results.append([g_name, top_name, score, correct])

    columns = [f"G name", "H name", "Score", "Correct"]
    with open("result.csv", 'w') as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(output_results)

    logger.info(f"Total time: {os.times()[0] - statr_time}")
