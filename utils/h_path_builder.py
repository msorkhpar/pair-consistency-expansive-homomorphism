import math

import networkx as nx

from lp.parameters import NodePair


def _find_paths(graph: nx.Graph):
    g = graph.to_undirected()

    paths = {}
    start = next(filter(lambda node: g.degree(node) != 2, g.nodes), None)
    if start is None:
        start = next(iter(g.nodes))
    stack: list[any, tuple[any, any]] = []
    visited = set()
    for start_neighbor in g.neighbors(start):
        if start_neighbor == start:
            continue
        stack.append((start_neighbor, (start, start_neighbor)))
        paths[(start, start_neighbor)] = []
    visited.add(start)

    while stack:
        node, path_name = stack.pop()
        branch_parent = path_name[0]

        if node not in visited:
            if not paths.get(path_name, None):
                paths[path_name] = [branch_parent]

            visited.add(node)
            paths[path_name].append(node)
            new_branch = False

            # if we reached to a none-degree two node, save the existing path
            # and continue with a new branch of this node's neighbors
            if len(paths[path_name]) > 1 and g.degree(node) != 2:
                new_branch = True

            # if we are not going to change to a new branch continue visiting the neighbors
            if new_branch:
                # if we are going to save the path and change the branch
                # put the neighbors into the stack with a path starting from current node
                for neighbor in g.neighbors(node):
                    if neighbor == node:
                        continue
                    if neighbor not in visited:
                        stack.append((neighbor, (node, neighbor)))

            else:
                for neighbor in g.neighbors(node):
                    if neighbor == node:
                        continue
                    stack.append((neighbor, path_name))

        else:
            # if there is a cycle of len 3 or more add it to the result
            if path_name in paths and len(paths[path_name]) > 1 and g.degree(node) != 2 \
                    and g.degree(paths[path_name][-1]) == 2:
                if len(paths[path_name]) == 2 and node == branch_parent:
                    continue
                if node in list(g.neighbors(paths[path_name][-1])):
                    paths[path_name].append(node)
    return {key: path for key, path in paths.items() if len(path) > 1}


def __generate_permutations_with_duplicates(elements, length, current=None):
    if current is None:
        current = []
    if len(current) == length:
        return [tuple(current)]

    permutations = []
    for element in elements:
        current.append(element)
        permutations.extend(__generate_permutations_with_duplicates(elements, length, current))
        current.pop()

    return permutations


def __build_path_graph(path: list[tuple[int, int]]) -> tuple[nx.Graph, float]:
    path_graph = nx.Graph()
    total_weight = 0
    for i in range(len(path) - 1):
        weight = math.dist(path[i], path[i + 1])
        path_graph.add_edge(path[i], path[i + 1], weight=weight)
        total_weight += weight

    return path_graph, total_weight


def build_degree_two_paths(h: nx.Graph) -> dict[tuple[tuple[int, int], tuple[int, int]], dict[str, any]]:
    paths = _find_paths(h)
    h_pairs = {}

    for key, path in paths.items():
        path_graph, path_weight = __build_path_graph(path)
        node_pairs = __generate_permutations_with_duplicates(path, 2)
        is_a_cycle = (path[0] == path[-1]) & len(path) > 2
        for i, j in node_pairs:
            if i == j and is_a_cycle:
                length = path_weight
                p = [i, i]
            else:
                length = nx.shortest_path_length(path_graph, i, j, weight="weight")
                p = nx.shortest_path(path_graph, i, j, weight="weight")
            h_pairs[(i, j)] = {"length": length, "path": p}

    return h_pairs
