import logging
import os
import sys
from multiprocessing import Pool, Manager

import cv2
import networkx as nx
from scipy.cluster.hierarchy import linkage, fcluster

from recognition.input_graph import InputGraph
from recognition.lp.solver import Solver
from recognition.mappings import mapper
from recognition.mappings.h_prime_builder import HPrime
import numpy as np

logging.basicConfig(filename='build_base_graphs.log', filemode='w',
                    format='%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
alpha = 2
beta = 3
gamma = 9
number_of_clusters = 10


def convert_graph_to_cv2_image(graph: nx.Graph, width: int, height: int, output_path: str = None, color=(0, 0, 0),
                               size: int = 1):
    output = np.ones((width, height, 3), np.uint8) * 255

    # Draw edges
    for u, v in graph.edges:
        x1, y1 = u
        x2, y2 = v
        cv2.line(output, (x1, y1), (x2, y2), (0, 0, 0), 1)
    for x, y in graph.nodes:
        cv2.circle(output, (x, y,), size, color, -1)

    cv2.imwrite(output_path, output)


def compare(base_graph: InputGraph, target_graph: InputGraph):
    costs = mapper.MapGtoH(base_graph, target_graph, alpha, beta, gamma).calculate_mapping_costs()
    solution = Solver(base_graph, target_graph, costs).solve()
    target_prime = HPrime(target_graph, solution)
    return costs, solution, target_prime


def get_cost(base, target, base_id, target_id, cached_costs: dict[tuple[int, int], float]):
    if base_id == target_id:
        cached_costs[(base_id, target_id)] = 0
    elif (base_id, target_id) not in cached_costs:
        _, base_target_solution, target_prime = compare(base, target)
        cost = base_target_solution.cost + base_target_solution.cost * (1 - target_prime.coverage)
        cached_costs[(base_id, target_id)] = cost

    return cached_costs[(base_id, target_id)]


def compute_graph_distance(g, h, g_index, h_index, cached_costs: dict[tuple[int, int], float]):
    return get_cost(g, h, g_index, h_index, cached_costs) + get_cost(h, g, h_index, g_index, cached_costs)


def worker(args):
    i, j, graph_i, graph_j, cached_costs = args
    distance = compute_graph_distance(graph_i, graph_j, i, j, cached_costs)
    return i, j, distance


input_directory = "2_base"
graph_paths = [os.path.join(input_directory, f) for f in os.listdir(input_directory)]
graphs: dict[int, InputGraph] = {index: InputGraph(path, True) for index, path in enumerate(graph_paths) if
                                 path.endswith(".adjlist")}
n_samples = len(graphs)

# Compute the distance matrix
if os.path.exists('2_base/distance_matrix.npy'):
    distance_matrix = np.load('2_base/distance_matrix.npy', allow_pickle=True)
else:
    distance_matrix = np.zeros((n_samples, n_samples))

    with Manager() as manager:
        cached_costs = manager.dict()
        for i in range(n_samples):
            logger.info(f"Computed distance matrix for graph {i + 1}/{n_samples}")
            # Include the shared dictionary in the processing queue
            processing_queue = [(i, j, graphs[i], graphs[j], cached_costs) for j in range(n_samples)]
            with Pool(processes=10) as pool:
                results = pool.map(worker, processing_queue)
            for i, j, distance in results:
                distance_matrix[i, j] = distance

    np.save('2_base/distance_matrix.npy', distance_matrix)

# Hierarchical clustering
Z = linkage(distance_matrix, method='complete')
labels = fcluster(Z, t=number_of_clusters, criterion='maxclust')  # t=10 to get 10 clusters

centroids = []
frequency = {}
for cluster_id in range(1, number_of_clusters + 1):  # Assuming labels are from 1 to 10
    cluster_indices = np.where(labels == cluster_id)[0]
    print(f"cluster[{cluster_id}] => has {len(cluster_indices)} items")
    frequency[cluster_id] = len(cluster_indices)

    avg_distances = []
    for idx in cluster_indices:
        avg_distance = np.mean([distance_matrix[idx, other_idx] for other_idx in cluster_indices])
        avg_distances.append(avg_distance)

    centroid_idx = cluster_indices[np.argmin(avg_distances)]
    centroids.append(graphs[centroid_idx])

sorted_frequency = sorted(frequency.items(), key=lambda x: x[1], reverse=True)

output_directory = "2_base_ground"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

for index, quantity in sorted_frequency[:number_of_clusters - 1]:
    rep_graph = centroids[index]
    output_path = os.path.join(output_directory, f"representative_{index}.adjlist")
    nx.write_adjlist(rep_graph.undirected_graph, output_path, delimiter="|")
    convert_graph_to_cv2_image(rep_graph.undirected_graph, 1024, 1024,
                               os.path.join(output_directory, f"{index}.png"),
                               color=(0, 0, 255), size=3)
