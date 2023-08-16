import math

import cv2
import networkx as nx
import numpy as np

from utils.config import Config

import logging
import os
from multiprocessing.pool import ThreadPool as Pool

from sklearn.datasets import fetch_openml

from reduction.path_reduction import remove_intermediary_nodes
from utils.config import Config
from utils.result_drawer import GraphDrawer

config = Config()
logger = logging.getLogger(__name__)


class GraphSimplifier:
    def _extract_graph_measurements(self):
        self.x1, self.y1 = np.inf, np.inf
        self.x2, self.y2 = -np.inf, -np.inf
        for x, y in self.graph.nodes:
            self.x1 = min(self.x1, x)
            self.y1 = min(self.y1, y)
            self.x2 = max(self.x2, x)
            self.y2 = max(self.y2, y)
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1

        self.width_factor = 1
        self.height_factor = 1

        if math.isinf(self.width) or self.width == 0:
            self.width = 1
            self.x1 = 0
        if math.isinf(self.height) or self.height == 0:
            self.height = 1
            self.y1 = 0

        if self.width > self.height:
            self.width_factor = self.config.image_width / self.width
            self.height_factor = self.config.image_height / self.width
        else:
            self.width_factor = self.config.image_width / self.height
            self.height_factor = self.config.image_height / self.height

    def _construct_graph(self, skeleton_path):
        skeleton = cv2.imread(skeleton_path, 0)
        rows = skeleton.shape[1]
        columns = skeleton.shape[0]
        skeleton_indices = np.where(skeleton > 0)
        y_indices, x_indices = skeleton_indices

        for x, y in zip(x_indices, y_indices):
            neighbors = [(x + dx, y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if (dx, dy) != (0, 0)]
            valid_neighbors = [(n_x, n_y) for n_x, n_y in neighbors if
                               0 <= n_x < rows and 0 <= n_y < columns and skeleton[n_y, n_x] > 0]
            self.graph.add_edges_from([((x, y), neighbor) for neighbor in valid_neighbors])

    def __init__(self, skeleton_path: str):
        self.config = Config()
        self.graph: nx.Graph = nx.Graph()
        self._construct_graph(skeleton_path)
        self._extract_graph_measurements()

    def reduce_graph_size(self):
        min_lower_bound_size = max(25, self.config.reducer_lower_bound_node_size)
        desired_upper_bound_size = max(self.config.reducer_upper_bound_node_size, min_lower_bound_size * 2)
        if self.graph.number_of_nodes() <= desired_upper_bound_size:
            return self.graph

        degree_2_nodes = {node for node, degree in self.graph.degree() if degree == 2}

        while self.graph.number_of_nodes() > desired_upper_bound_size:
            candidates = degree_2_nodes.copy()
            nodes_to_remove = set()
            while len(candidates) > 0:
                node = candidates.pop()
                neighbors = list(self.graph.neighbors(node))
                self.graph.add_edge(neighbors[0], neighbors[1])
                nodes_to_remove.add(node)
                degree_2_nodes.remove(node)
                candidates.difference_update(neighbors)
            if self.graph.number_of_nodes() - len(nodes_to_remove) < min_lower_bound_size:
                break
            self.graph.remove_nodes_from(nodes_to_remove)
        return self.graph

    def process_small_edges(self, threshold: float, merge_mode: bool):
        while True:
            if merge_mode:
                edges_with_weight_less_than_threshold = [
                    (u, v) for u, v in self.graph.edges()
                    if math.dist(u, v) < threshold
                ]
            else:
                edges_with_weight_less_than_threshold = [
                    (u, v) for u, v in self.graph.edges()
                    if math.dist(u, v) < threshold and (
                            self.graph.degree(u) == 2 or self.graph.degree(v) == 2
                    )
                ]

            if not edges_with_weight_less_than_threshold:
                break

            to_remove_nodes = set()
            for (u, v) in edges_with_weight_less_than_threshold:
                if not merge_mode and self.graph.degree(u) != 2 and self.graph.degree(v) != 2:
                    continue
                if self.graph.degree(u) > self.graph.degree(v):
                    u, v = v, u
                u_neighbors = list(self.graph.neighbors(u))
                for neighbor in u_neighbors:
                    if v == neighbor:
                        continue
                    self.graph.add_edge(v, neighbor, weight=math.dist(v, neighbor))
                to_remove_nodes.add(u)
            self.graph.remove_nodes_from(to_remove_nodes)

    def remove_isolated_nodes(self):
        isolated_nodes = [node for node in self.graph.nodes() if self.graph.degree(node) == 0]
        self.graph.remove_nodes_from(isolated_nodes)

    def scale(self):
        mapping = dict()
        shift_x = int((self.config.image_width - (self.width * self.width_factor)) / 2)
        shift_y = int((self.config.image_height - (self.height * self.height_factor)) / 2)
        for x, y in self.graph.nodes():
            scaled_x = math.floor((x - self.x1) * self.width_factor) + shift_x
            scaled_y = math.floor((y - self.y1) * self.height_factor) + shift_y
            mapping.update({
                (x, y): (scaled_x, scaled_y)
            })
        self.graph = nx.relabel_nodes(self.graph, mapping)

    def save_graph_to_file(self, destination_path):
        nx.write_adjlist(self.graph, destination_path, delimiter="|")


def worker(args):
    idx, skeleton_path, graph_path, graph_image_path = args
    if idx % 1000 == 0:
        logger.info(f"Processing {idx // 1000}k/70k...")
    graph_processor = GraphSimplifier(skeleton_path)
    graph_processor.reduce_graph_size()
    graph_processor.process_small_edges(config.small_edge_merger_threshold, True)
    remove_intermediary_nodes(graph_processor.graph, config.intermediary_node_remover_threshold)
    graph_processor.process_small_edges(config.small_edge_remover_threshold_1, False)
    graph_processor.process_small_edges(config.small_edge_remover_threshold_2, False)
    graph_processor.remove_isolated_nodes()
    graph_processor.scale()
    graph_processor.save_graph_to_file(graph_path)
    GraphDrawer(graph_processor.graph, graph_image_path).convert_graph_to_cv2_image(color=(0, 0, 255))


def reduce_graphs_edges(labels):
    logger.info(f"Simplifying...")
    for i in range(70):
        os.makedirs(os.path.join(config.graphs_dir, str(i)), exist_ok=True)

    processing_queue = []
    for idx in range(len(labels)):
        label = labels[idx]
        skeleton_path = os.path.join(config.mnist_skeletons_dir, str(idx // 1000), f'{label}_{idx}.png')
        graph_path = os.path.join(config.graphs_dir, str(idx // 1000), f'{label}_{idx}.adjlist')
        graph_image_path = os.path.join(config.graphs_dir, str(idx // 1000), f'{label}_{idx}.png')
        if os.path.exists(graph_path) or not os.path.exists(skeleton_path):
            continue
        processing_queue.append((idx, skeleton_path, graph_path, graph_image_path))

    with Pool(processes=config.processors_limit) as pool:
        pool.map(worker, processing_queue)
