import math

from recognition.mappings.node_pair import NodePair
from utils.graph_frame_finder import find_aspect_ratio
from utils.path_builder import build_degree_two_paths
from utils.nxgraph_reader import construct_nxgraphs


class InputGraph:
    def _total_length(self):
        total_length = 0
        min_length = math.inf
        for u, v in self.undirected_graph.edges():
            weight = math.dist(u, v)
            total_length += weight
            if min_length > weight and weight > 0:
                min_length = weight
        if total_length == 0:
            return 1, 1
        return total_length, min_length

    def _construct_paths(self) -> dict[tuple[tuple[int, int], tuple[int, int]], NodePair]:
        return {(i, j): NodePair((i, j), data["length"], data["path"]) for (i, j), data in
                build_degree_two_paths(self.undirected_graph, self.use_paths).items()}

    def _construct_node_appearance(self) -> dict[tuple[int, int], set[NodePair]]:
        result = dict()
        for node_pair in self._paths.values():
            path = node_pair.path
            for node in path:
                if result.get(node) is None:
                    result[node] = set()
                result[node].add(node_pair)
        return result

    def __init__(self, adjacency_list_path: str, use_paths: bool = False, label_postfix: str = "", name: str = "",
                 digit: int = None):
        self.digit = digit
        self.name = name
        self.adjacency_list_path = adjacency_list_path
        self.undirected_graph, self.directed_graph, self.self_loop_graph = construct_nxgraphs(
            adjacency_list_path, label_postfix
        )
        self.aspect_ratio = find_aspect_ratio(self.undirected_graph)
        self.total_length, self.min_length = self._total_length()
        self.use_paths = use_paths
        self._paths: dict[tuple[tuple[int, int], tuple[int, int]], NodePair] = self._construct_paths()
        self._paths_set: set[NodePair] = set(self._paths.values())
        self.node_in_paths_dict: dict[tuple[int, int], set[NodePair]] = self._construct_node_appearance()

    def edges(self, directed: bool = False, self_loop: bool = False) -> list[NodePair]:
        target_graph = self.undirected_graph
        if directed and self_loop:
            target_graph = self.self_loop_graph
        elif directed:
            target_graph = self.directed_graph
        return list([NodePair((v1, v2)) for v1, v2 in target_graph.edges()])

    def neighbors(self) -> dict[tuple[int, int], list[tuple[int, int]]]:
        neighbors_dict = {}
        for node in self.directed_graph.nodes():
            neighbors_dict[node] = list(self.directed_graph.neighbors(node))
        return neighbors_dict

    def path(self, ij: tuple[tuple[int, int], tuple[int, int]]) -> NodePair:
        return self._paths[ij]

    def paths(self) -> set[NodePair]:
        return self._paths_set

    def node_participation(self) -> dict[tuple[int, int], set[NodePair]]:
        return self.node_in_paths_dict
