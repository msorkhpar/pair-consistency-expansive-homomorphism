import networkx as nx


def _assign_name_to_node(names, counter, node):
    if node not in names:
        names[node] = chr(counter)
        counter += 1
    return counter


def __assign_names_to_nodes(names, counter, graph: nx.Graph):
    for node in graph.nodes:
        counter = _assign_name_to_node(names, counter, node)
    return counter


def generate_node_labels(G: nx.Graph, H: nx.Graph):
    counter = 97
    names = {}
    counter = __assign_names_to_nodes(names, counter, G)
    counter = __assign_names_to_nodes(names, counter, H)
    return names
