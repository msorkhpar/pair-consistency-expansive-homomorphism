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

logger = logging.getLogger(__name__)
alpha = 0.6  # distance
beta = 0.4  # length
use_paths = False


def __graph_to_image(u_h, mappings) -> nx.Graph:
    h_edge_pairs = {(i, j): NodePair((i, j), data["length"], data["path"]) for (i, j), data in
                    build_degree_two_paths(u_h, use_paths).items()}
    graph_to_image = nx.Graph()
    for key in mappings.keys():
        u, v, i, j = key.e1.v1, key.e1.v2, key.e2.v1, key.e2.v2
        path = h_edge_pairs[(i, j)].path
        for n_index in range(len(path) - 1):
            p1 = path[n_index]
            p2 = path[n_index + 1]
            weight = h_edge_pairs[p1, p2].length
            if graph_to_image.has_edge(p1, p2):
                graph_to_image[p1][p2]["weight"] += weight
            else:
                graph_to_image.add_edge(p1, p2, weight=weight)

    return graph_to_image


def __compare(dg, d_l_h, u_h):
    h_edge_pairs = {(i, j): NodePair((i, j), data["length"], data["path"]) for (i, j), data in
                    build_degree_two_paths(u_h, use_paths).items()}

    g_to_h_costs: dict[EdgeMap, dict[str, float]] = calculate_mapping_cost(dg, d_l_h, list(h_edge_pairs.values()),
                                                                           alpha, beta)
    solver_g_to_h_solver = Solver(dg, d_l_h, list(h_edge_pairs.values()), g_to_h_costs)
    g_to_h = solver_g_to_h_solver.solve()
    logger.info(g_to_h)
    solver_g_to_h_solver.clear()

    mappings = {}
    for key in g_to_h.variables.keys():
        u, v, i, j = key.e1.v1, key.e1.v2, key.e2.v1, key.e2.v2
        dual_key = EdgeMap(NodePair((v, u)), NodePair((j, i)))
        if mappings.get(dual_key) is None:
            mappings[key] = g_to_h_costs[key]
    return mappings, g_to_h.cost


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

    directed_g = construct_nxgraph(config.g_graph_path, type=nx.DiGraph)
    directed_loop_g = construct_nxgraph(config.g_graph_path, type=nx.DiGraph, add_self_loops=True)
    undirected_g = construct_nxgraph(config.g_graph_path)
    assign_edge_weights(undirected_g)

    result = []
    counter = 0
    for root, directories, h_adjlists in os.walk(config.computerized_graphs_dir):
        for h_adjlist in h_adjlists:
            counter += 1
            h_adjlist_path = os.path.join(root, h_adjlist)
            h_name = h_adjlist.split(".")[0]
            directed_loop_h = construct_nxgraph(h_adjlist_path, type=nx.DiGraph, add_self_loops=True)
            directed_h = construct_nxgraph(h_adjlist_path, type=nx.DiGraph)
            undirected_h = construct_nxgraph(h_adjlist_path)
            assign_edge_weights(undirected_h)
            # g_with_h_similarity = similarity(undirected_g, undirected_h)

            g_to_h_mappings, g_to_h_cost = __compare(directed_g, directed_loop_h, undirected_h)
            h_prime = __graph_to_image(undirected_h, g_to_h_mappings)
            # h_with_i_similarity = __graph_to_image_similarity(undirected_h, g_to_h_mappings)

            h_to_g_mappings, h_to_g_cost = __compare(directed_h, directed_loop_g, undirected_g)
            g_prime = __graph_to_image(undirected_g, h_to_g_mappings)

            # g_with_i_prime_similarity = __graph_to_image_similarity(undirected_g, h_to_g_mappings)
            # h_with_i_prime_similarity = __graph_to_image_similarity(undirected_h, h_to_g_mappings)

            draw_LP_result(undirected_g, undirected_h, os.path.join(output_path, f"{h_name}.png"), g_to_h_mappings,
                           h_to_g_mappings, h_prime, g_prime)

            # h_g_h_sim = similarity(undirected_h, i_graph)
            # h_h_to_g_sim = similarity(undirected_g, i_prime_graph)
            h_with_h_prime_similarity = similarity(undirected_h, h_prime)
            g_with_g_prime_similarity = similarity(undirected_g, g_prime)
            result.append(
                [
                    h_name,
                    round(g_to_h_cost, 2),
                    round(h_to_g_cost, 2),
                    h_with_h_prime_similarity,
                    g_with_g_prime_similarity
                    # round(g_with_h_similarity, 2),
                    # round(g_with_i_similarity, 2),
                    # round(h_with_i_similarity, 2),
                    # round(g_with_i_prime_similarity, 2),
                    # round(h_with_i_prime_similarity, 2)
                ]
            )

    columns = [
        f"'{config.g_graph_path}' {'to H paths' if use_paths else 'to H edges'}", "Cost_LP(G,H)", "Cost_LP(H,G)",
        "Sim(H & H')", "Sim(G & G')"
        # "Sim(G & H)", "Sim(G & I)", "Sim(H & I)","Sim(G & I')", "Sim(H & I')"
    ]
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
            # if column not in ["Cost_LP(G,H)", "Cost_LP(H,G)"]:
            #     min_value = 0
            df_normalized[column] = round((df_normalized[column]) / max_value, 2)

    lp_g_h_c = df_normalized[df_normalized.columns[1]]
    lp_h_g_c = df_normalized[df_normalized.columns[2]]
    s_h_h_prime = df_normalized[df_normalized.columns[3]]
    s_g_g_prime = df_normalized[df_normalized.columns[4]]
    # s_g_h = df_normalized[df_normalized.columns[3]]
    # s_g_i = df_normalized[df_normalized.columns[4]]
    # s_h_i = df_normalized[df_normalized.columns[5]]
    # s_g_i_prime = df_normalized[df_normalized.columns[6]]
    # s_h_i_prime = df_normalized[df_normalized.columns[7]]

    score = (
            .2 * lp_g_h_c +
            .2 * lp_h_g_c +
            .3 * s_h_h_prime +
            .3 * s_g_g_prime
    )
    df_normalized['Score'] = round(score, 3)
    df_normalized.sort_values(by='Score', ascending=True, inplace=True)

    df_normalized.to_csv(os.path.join(output_path, "normalized_result.csv"), index=False)
