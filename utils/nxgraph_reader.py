import math

import networkx as nx


def _convert_node(node_str: str) -> tuple[int, int]:
    result = map(str.strip, node_str.strip("()").split(","))
    x, y = map(int, result)
    return x, y


def _assign_edge_weights(graph: nx.Graph):
    for u, v in graph.edges:
        weight_value = math.dist(u, v)
        graph.edges[u, v]['weight'] = weight_value


def _assign_label_to_nodes(graph: nx.Graph, postfix):
    counter = 97
    for node, data in graph.nodes(data=True):
        data['label'] = chr(counter) + postfix
        counter += 1


def construct_nxgraphs(adjacency_list_path, label_postfix="") -> tuple[nx.Graph, nx.DiGraph, nx.DiGraph]:
    # construct undirected graph
    undirected_graph = nx.read_adjlist(adjacency_list_path, create_using=nx.Graph, delimiter="|",
                                       nodetype=_convert_node)
    # assign a label to each node
    _assign_label_to_nodes(undirected_graph, label_postfix)

    # construct directed graph from undirected graph
    directed_graph = nx.DiGraph(undirected_graph)

    # construct self-loop directed graph from directed graph
    self_loop_graph = nx.DiGraph(directed_graph)
    for node in list(directed_graph.nodes()):
        self_loop_graph.add_edge(node, node)

    # assign edge weights to the graphs
    _assign_edge_weights(undirected_graph)
    _assign_edge_weights(directed_graph)
    _assign_edge_weights(self_loop_graph)

    return undirected_graph, directed_graph, self_loop_graph
