import math

import networkx as nx


def assign_edge_weights(graph: nx.Graph):
    for u, v in graph.edges:
        weight_value = math.dist(u, v)
        graph.edges[u, v]['weight'] = weight_value
        if graph.has_edge(v, u):
            graph.edges[v, u]['weight'] = weight_value
