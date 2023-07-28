import networkx as nx


def _convert_node(node_str: str) -> tuple[int, int]:
    result = map(str.strip, node_str.strip("()").split(","))
    x, y = map(int, result)
    return x, y


def construct_nxgraph(graph_path) -> nx.Graph:
    return nx.read_adjlist(graph_path, create_using=nx.Graph, delimiter="|", nodetype=_convert_node)
