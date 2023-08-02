import csv
import logging
import networkx as nx
import pandas as pd

from cost_function.self_loop_cost import calculate_self_loop_cost
from cost_function.mapping_cost import calculate_mapping_cost

import logging

import os
import shutil

from lp.parameters import EdgeMap, NodePair
from lp.solver import Solver
from similarity_check.eigenvector_similarity import similarity
from utils.assign_weight_to_edges import assign_edge_weights
from utils.config import Config
from utils.h_path_builder import build_degree_two_paths
from utils.nxgraph_reader import construct_nxgraph
from utils.result_drawer import draw_LP_result

if __name__ == '__main__':
    alpha = 0.7  # distance
    beta = 0.3  # length

    config = Config()
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=config.log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Loaded configurations:{config}")
    output_path = "./output"
    shutil.rmtree(output_path, ignore_errors=True)
    os.makedirs(output_path)

    G = construct_nxgraph(config.g_graph_path, type=nx.DiGraph)
    undirected_G = construct_nxgraph(config.g_graph_path)
    assign_edge_weights(undirected_G)

    result = []
    counter = 0
    for root, directories, h_adjlists in os.walk(config.computerized_graphs_dir):
        for h_adjlist in h_adjlists:
            counter += 1
            h_adjlist_path = os.path.join(root, h_adjlist)
            h_name = h_adjlist.split(".")[0]
            H = construct_nxgraph(h_adjlist_path, type=nx.DiGraph, add_self_loops=True)
            undirected_H = construct_nxgraph(h_adjlist_path)
            assign_edge_weights(undirected_H)

            starting_similarity_value_g_to_h = similarity(undirected_G, undirected_H)
            # starting_similarity_value_h_to_g = similarity(undirected_H, undirected_)

            logger.info(f"Running against {h_name}")
            h_edge_pairs = [NodePair((i, j), length) for (i, j), length in build_degree_two_paths(undirected_H).items()]

            g_to_h_costs: dict[EdgeMap, dict[str, float]] = calculate_mapping_cost(G, H, h_edge_pairs, alpha, beta)
            solver_g_to_h_solver = Solver(G, H, h_edge_pairs, g_to_h_costs)
            g_to_h = solver_g_to_h_solver.solve()
            logger.info(g_to_h)
            solver_g_to_h_solver.clear()

            winner_costs_g_to_h = {}
            for key in g_to_h.variables.keys():
                u, v, i, j = key.e1.v1, key.e1.v2, key.e2.v1, key.e2.v2
                dual_key = EdgeMap(NodePair((v, u)), NodePair((j, i)))
                if winner_costs_g_to_h.get(dual_key) is None:
                    winner_costs_g_to_h[key] = g_to_h_costs[key]

            draw_LP_result(G, H, os.path.join(output_path, f"{h_name}.png"), winner_costs_g_to_h)

            mapped_subgraph = nx.Graph()
            for key in winner_costs_g_to_h.keys():
                u, v, i, j = key.e1.v1, key.e1.v2, key.e2.v1, key.e2.v2
                mapped_subgraph.add_edge(i, j)

            assign_edge_weights(mapped_subgraph)
            similarity_value = similarity(undirected_G, mapped_subgraph)

            result.append([
                h_name,
                round(g_to_h.cost, 2),
                round(starting_similarity_value_g_to_h, 2),
                round(similarity_value, 2)
            ])

    with open(os.path.join(output_path, "result.csv"), 'w') as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Name of the target file", "G to H LP cost", "G&H similarity", "G&I Similarity Value"])
        writer.writerows(result)

    input_file = f"{output_path}/result.csv"
    df = pd.read_csv(input_file)

    # Step 2: Normalize each column based on its maximum value
    df_normalized = df.copy()
    for column in df_normalized.columns[1:]:
        max = df_normalized[column].max()
        if max == 0:
            df_normalized[column] = 0
        else:
            df_normalized[column] = round(df_normalized[column] / df_normalized[column].max(), 2)

    first_normalized_col = df_normalized[df_normalized.columns[1]]
    second_normalized_col = df_normalized[df_normalized.columns[2]]
    third_normalized_col = df_normalized[df_normalized.columns[3]]

    new_column = 0.2 * first_normalized_col + 0.3 * second_normalized_col + 0.5 * abs(
        second_normalized_col - third_normalized_col)
    df_normalized['Score'] = 1 - round(new_column, 2)
    df_normalized.sort_values(by='Score', ascending=False, inplace=True)

    # Step 4: Save the normalized DataFrame to a new CSV file
    df_normalized.to_csv(f"{output_path}/normalized_result.csv", index=False)
