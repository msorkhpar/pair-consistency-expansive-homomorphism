import networkx as nx


def transport_to_cartesian_system(G: nx.Graph, input_width: int, input_height: int):
    def _get_cartesian_point(column, row, width, height):
        x = column - (width / 2)
        y = -(row - (height / 2))
        return x, y

    cartesian_labels = {node: _get_cartesian_point(node[0], node[1], input_width, input_height) for node in G}
    labels = {cartesian_labels[node]: node for node in cartesian_labels}
    return nx.relabel_nodes(G, cartesian_labels), labels
