import concurrent
import logging
import os
import concurrent.futures
from multiprocessing import Manager
from threading import Lock
from typing import List

import networkx as nx
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster

from recognition.digit_detector import compare
from recognition.input_graph import InputGraph
from utils.config import Config

config = Config()
logger = logging.getLogger(__name__)


def _get_cost(base, target, base_id, target_id, cached_costs: dict[tuple[int, int], float]):
    if base_id == target_id:
        cached_costs[(base_id, target_id)] = 0
    elif (base_id, target_id) not in cached_costs:
        _, base_to_target_solution, target_prime = compare(base, target)
        if base_to_target_solution is None:
            cost = -1
        else:
            cost = base_to_target_solution.cost + base_to_target_solution.cost * (1 - target_prime.coverage)
        cached_costs[(base_id, target_id)] = cost
    return cached_costs[(base_id, target_id)]


def _compute_graph_distance(g, h, g_index, h_index, cached_costs: dict[tuple[int, int], float]):
    return _get_cost(g, h, g_index, h_index, cached_costs) + _get_cost(h, g, h_index, g_index, cached_costs)


def _distance(i, j, graph_i, graph_j, cached_costs):
    distance = _compute_graph_distance(graph_i, graph_j, i, j, cached_costs)
    return i, j, distance


def calculate_cost_concurrently(args):
    try:
        c_i, graphs, cache_costs = args
        return [_distance(c_i, c_j, graphs[c_i], graphs[c_j], cache_costs) for c_j in range(len(graphs))]
    except Exception as e:
        print(f"Error in getting the distance: {e}")
        return []


def _construct_distance_matrix(graphs: List[InputGraph]):
    n = len(graphs)
    distance_matrix = np.zeros((n, n))
    cached_costs = {}
    for c_i in range(n):
        results = [
            _distance(c_i, c_j, graphs[c_i], graphs[c_j], cached_costs) for c_j in
            range(n)
        ]
        for i, j, distance in results:
            distance_matrix[i, j] = distance
    return distance_matrix


def _cluster(distance_matrix, graphs) -> List[InputGraph]:
    Z = linkage(distance_matrix, method='complete')
    labels = fcluster(Z, t=config.number_of_clusters, criterion='maxclust')

    centroids = []
    frequency = {}

    for cluster_id in range(1, config.number_of_clusters + 1):
        cluster_indices = np.where(labels == cluster_id)[0]
        if len(cluster_indices) == 0:
            continue
        frequency[cluster_id] = len(cluster_indices)
        avg_distances = []
        for idx in cluster_indices:
            avg_distance = np.mean([distance_matrix[idx, other_idx] for other_idx in cluster_indices])
            avg_distances.append(avg_distance)

        centroid_idx = cluster_indices[np.argmin(avg_distances)]
        centroids.append(graphs[centroid_idx])

    sorted_frequency = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
    cluster_id_to_index = {cluster_id: idx for idx, cluster_id in enumerate(range(1, config.number_of_clusters + 1))}

    nominates = []
    for cluster_id, quantity in sorted_frequency[:config.top_n_clusters]:
        idx = cluster_id_to_index[cluster_id]
        rep_graph: InputGraph = centroids[idx]
        nominates.append(rep_graph)
    return nominates


def _pick_cluster_nominates(digit: int, digit_samples: List[int]) -> List[InputGraph]:
    logger.info(f"Creating distance matrix for digit [{digit}]...")
    graphs = []
    for j in range(config.number_of_samples):
        idx = digit_samples[j]
        graph = InputGraph(
            os.path.join(config.graphs_dir, str(idx // 1000), f'{digit}_{idx}.adjlist'), True,
            name=f"{digit}_{idx}", digit=digit
        )
        if graph.undirected_graph.number_of_nodes() > 1 and nx.number_connected_components(graph.undirected_graph) == 1:
            graphs.append(graph)
    distance_matrix = _construct_distance_matrix(graphs)
    logger.info(f"Distance matrix for digit [{digit}] is constructed.")
    nominates = _cluster(distance_matrix, graphs)
    logger.info(f"Digit [{digit}] will have [{len(nominates)}] representatives graphs.")
    return nominates


def get_nominates(digit_samples: dict[int, list[int]]) -> list[InputGraph]:
    nominates = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=config.processors_limit) as executor:
        futures = [executor.submit(_pick_cluster_nominates, i, digit_samples[i]) for i in range(10)]
        for i, future in enumerate(futures):
            nominates += future.result()
    return nominates