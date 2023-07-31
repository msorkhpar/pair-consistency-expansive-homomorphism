import networkx as nx


def _convert_node(node_str: str) -> tuple[int, int]:
    result = map(str.strip, node_str.strip("()").split(","))
    x, y = map(int, result)
    return x, y

def construct_nxgraph(graph_path, type=nx.Graph, add_self_loops=False) -> nx.Graph | nx.DiGraph:
    graph = nx.read_adjlist(graph_path, create_using=type, delimiter="|", nodetype=_convert_node)
    if type == nx.DiGraph:
        for uv in list(graph.edges()):
            u, v = uv
            graph.add_edge(v, u)
            if add_self_loops:
                graph.add_edge(u, u)
                graph.add_edge(v, v)


    return graph
