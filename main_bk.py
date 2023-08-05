# import csv
# import logging
# import math
#
# import networkx as nx
# import pandas as pd
#
# from cost_function.mapping_cost import calculate_mapping_cost
#
# import logging
#
# import os
# import shutil
#
# from g_to_h_mapper import map_g_to_h
# from utils.assign_weight_to_edges import assign_edge_weights
# from utils.config import Config
# from utils.graph_frame_finder import find_aspect_ratio
# from utils.nxgraph_reader import construct_nxgraph
# from utils.result_drawer import draw_LP_result
#
# logger = logging.getLogger(__name__)
# alpha = 2
# beta = 3
# gamma = 9
#
# use_path_g_to_h = True
# use_path_h_to_g = True
#
# if __name__ == '__main__':
#
#     config = Config()
#     logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s',
#                         datefmt='%Y-%m-%d %H:%M:%S',
#                         level=config.log_level)
#     logger = logging.getLogger(__name__)
#
#     logger.info(f"Loaded configurations:{config}")
#     output_path = "./output"
#     shutil.rmtree(output_path, ignore_errors=True)
#     os.makedirs(output_path)
#
#     directed_g = construct_nxgraph(config.g_graph_path, type=nx.DiGraph)
#     directed_loop_g = construct_nxgraph(config.g_graph_path, type=nx.DiGraph, add_self_loops=True)
#     undirected_g = construct_nxgraph(config.g_graph_path)
#     assign_edge_weights(undirected_g)
#     g_aspect_ratio = find_aspect_ratio(undirected_g)
#
#     result = []
#     for root, directories, h_adjlists in os.walk(config.computerized_graphs_dir):
#         for h_adjlist in h_adjlists:
#             h_adjlist_path = os.path.join(root, h_adjlist)
#             h_name = h_adjlist.split(".")[0]
#             directed_loop_h = construct_nxgraph(h_adjlist_path, type=nx.DiGraph, add_self_loops=True)
#             directed_h = construct_nxgraph(h_adjlist_path, type=nx.DiGraph)
#             undirected_h = construct_nxgraph(h_adjlist_path)
#             assign_edge_weights(undirected_h)
#             h_aspect_ratio = find_aspect_ratio(undirected_h)
#
#             g_to_h_mappings, g_to_h_cost, h_prime, h_prime_coverage = map_g_to_h(directed_g, directed_loop_h,
#                                                                                  undirected_h, g_aspect_ratio,
#                                                                                  h_aspect_ratio, alpha, beta, gamma,
#                                                                                  use_path_g_to_h)
#
#             h_to_g_mappings, h_to_g_cost, g_prime, g_prime_coverage = map_g_to_h(directed_h, directed_loop_g,
#                                                                                  undirected_g, h_aspect_ratio,
#                                                                                  g_aspect_ratio, alpha, beta, gamma,
#                                                                                  use_path_h_to_g)
#
#             draw_LP_result(undirected_g, undirected_h, os.path.join(output_path, f"{h_name}.png"), g_to_h_mappings,
#                            h_to_g_mappings, h_prime, g_prime)
#
#             result.append(
#                 [
#                     h_name,
#                     g_to_h_cost,
#                     h_to_g_cost,
#                     g_prime_coverage,
#                     h_prime_coverage
#                 ]
#             )
#
#     columns = [f"{config.g_graph_path} To Target", "Cost_LP(G,H)", "Cost_LP(H,G)", "G' Coverage", "H' Coverage"]
#     with open(os.path.join(output_path, "result.csv"), 'w') as file:
#         writer = csv.writer(file)
#         writer.writerow(columns)
#         writer.writerows(result)
#
#     df = pd.DataFrame(result, columns=columns)
#
#     df_normalized = df.copy()
#     for column in df_normalized.columns[1:]:
#         max_value = df_normalized[column].max()
#         min_value = df_normalized[column].min()
#         if max_value == 0:
#             df_normalized[column] = 0
#         else:
#             df_normalized[column] = round(df_normalized[column], 2)
#
#     g_to_h_cost = df_normalized[df_normalized.columns[1]]
#     h_to_g_cost = df_normalized[df_normalized.columns[2]]
#     g_prime_coverage = df_normalized[df_normalized.columns[3]]
#     h_prime_coverage = df_normalized[df_normalized.columns[4]]
#
#     score = g_to_h_cost + g_to_h_cost * (1 - h_prime_coverage) + h_to_g_cost + h_to_g_cost * (1 - g_prime_coverage)
#     df_normalized['Score'] = round(score, 3)
#     df_normalized.sort_values(by='Score', ascending=True, inplace=True)
#
#     df_normalized.to_csv(os.path.join(output_path, "normalized_result.csv"), index=False)
