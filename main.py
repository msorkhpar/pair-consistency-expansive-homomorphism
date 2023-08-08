import csv
import logging
import math

import networkx as nx
import pandas as pd

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

use_path_in_g_prime = True
use_path_in_h_prime = True


def compare(base_graph: InputGraph, target_graph: InputGraph):
    costs = mapper.MapGtoH(base_graph, target_graph, alpha, beta, gamma).calculate_mapping_costs()
    solution = Solver(base_graph, target_graph, costs).solve()
    target_prime = HPrime(target_graph, solution)
    return costs, solution, target_prime


if __name__ == '__main__':
    statr_time = os.times()[0]
    config = Config()
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=config.log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Loaded configurations:{config}")
    output_path = "./output"
    shutil.rmtree(output_path, ignore_errors=True)
    os.makedirs(output_path)

    g = InputGraph(config.g_graph_path, use_path_in_g_prime)

    result = []
    for root, directories, h_adjlists in os.walk(config.computerized_graphs_dir):
        for h_adjlist in h_adjlists:
            h_adjlist_path = os.path.join(root, h_adjlist)
            h_name = h_adjlist.split(".")[0]
            h = InputGraph(h_adjlist_path, use_path_in_h_prime, "'")

            g_h_costs, g_h_solution, h_prime = compare(g, h)
            logger.info(g_h_solution)

            h_g_costs, h_g_solution, g_prime = compare(h, g)
            logger.info(h_g_solution)
            if config.generate_mapping_diagrams:
                MappingDrawer(os.path.join(output_path, f"{h_name}.png"), g.undirected_graph, h.undirected_graph,
                              h_prime.prime_graph, g_h_solution.variables, g_prime.prime_graph,
                              h_g_solution.variables).draw()

            result.append([
                h_name, g_h_solution.cost, h_g_solution.cost, g_prime.coverage, h_prime.coverage
            ])

    columns = [f"{config.g_graph_path} To Target", "Cost_LP(G,H)", "Cost_LP(H,G)", "G' Coverage", "H' Coverage"]
    with open(os.path.join(output_path, "result.csv"), 'w') as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(result)

    df = pd.DataFrame(result, columns=columns)

    df_normalized = df.copy()
    for column in df_normalized.columns[1:]:
        max_value = df_normalized[column].max()
        min_value = df_normalized[column].min()
        if max_value == 0:
            df_normalized[column] = 0
        else:
            df_normalized[column] = round(df_normalized[column], 2)

    g_h_cost = df_normalized[df_normalized.columns[1]]
    h_g_cost = df_normalized[df_normalized.columns[2]]
    g_prime_coverage = df_normalized[df_normalized.columns[3]]
    h_prime_coverage = df_normalized[df_normalized.columns[4]]

    score = g_h_cost + g_h_cost * (1 - h_prime_coverage) + h_g_cost + h_g_cost * (1 - g_prime_coverage)
    df_normalized['Score'] = round(score, 3)
    df_normalized.sort_values(by='Score', ascending=True, inplace=True)

    df_normalized.to_csv(os.path.join(output_path, "normalized_result.csv"), index=False)
    logger.info(f"Total time: {os.times()[0] - statr_time}")
    logger.info("*"*50)
    for index, rank_name in [(0, "Fist"), (1, "Second"), (2, "Third")]:
        logger.info(f"{rank_name} rank is: {df_normalized.iloc[index][0]} = {df_normalized.iloc[index][5]}")
