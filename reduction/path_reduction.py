import math

import networkx as nx

from utils.path_builder import find_paths
from utils.mathematics import distance_from_path_percentage


def _is_good_path(path, percentage):
    u = path[0]
    v = path[-1]
    for i in range(1, len(path) - 1):
        w = path[i]
        if distance_from_path_percentage(u, v, w) > percentage:
            return False
    return True


def _construct_good_paths(P, start, end, percentage):
    bfs_path = nx.shortest_path(P, start, end)
    all_pairs = dict(nx.all_pairs_shortest_path(P))
    good_paths = list()
    for i in range(len(bfs_path) - 2):
        for j in range(i + 2, len(bfs_path)):
            path = all_pairs[bfs_path[i]][bfs_path[j]]
            weight = math.dist(path[0], path[-1])
            if _is_good_path(path, percentage):
                good_paths.append((weight, path))
            if j - i > 5:
                break
    good_paths.sort(reverse=True)
    return good_paths


def remove_intermediary_nodes(G: nx.Graph, percentage: float):
    none_degree_twos_counter = sum(1 for node in G.nodes() if G.degree(node) != 2)

    dfs_paths = find_paths(G)
    for key, dfs_path in dfs_paths.items():
        path_graph = nx.DiGraph()
        start = dfs_path[0]
        end = dfs_path[-1]
        if start == end:
            end = dfs_path[-2]
        for i in range(len(dfs_path) - 1):
            source = dfs_path[i]
            target = dfs_path[i + 1]
            path_graph.add_edge(source, target)

        good_paths = _construct_good_paths(path_graph, start, end, percentage)
        while good_paths:
            for weight, path in good_paths:
                if set(path).issubset(set(path_graph.nodes())):
                    path_graph.remove_nodes_from(path[1:-1])
                    path_graph.add_edge(path[0], path[-1])
                    G.remove_nodes_from(path[1:-1])
                    G.add_edge(path[0], path[-1])
            good_paths = _construct_good_paths(path_graph, start, end, percentage)

        if none_degree_twos_counter != sum(1 for node in G.nodes() if G.degree(node) != 2):
            remove_intermediary_nodes(G, percentage)
