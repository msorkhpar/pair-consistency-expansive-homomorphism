import networkx as nx


def _convert_node(node_str: str) -> tuple[int, int]:
    result = map(str.strip, node_str.strip("()").split(","))
    x, y = map(int, result)
    return x, y


def construct_nxgraph(graph_path, type=nx.Graph, add_self_loops=False) -> nx.Graph | nx.DiGraph:
    G = nx.read_adjlist(graph_path, create_using=type, delimiter="|", nodetype=_convert_node)
    if type == nx.DiGraph:
        for uv in list(G.edges()):
            u, v = uv
            G.add_edge(v, u)
    if add_self_loops:
        for node in G.nodes():
            G.add_edge(node, node)
    return G
