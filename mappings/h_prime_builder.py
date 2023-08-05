from input_graph import InputGraph
from solution import Solution
import networkx as nx


class HPrime:
    def __init__(self, h: InputGraph, solution: Solution):
        self.prime_graph = nx.Graph()
        h_prime_length = 0
        for key in solution.variables.keys():
            u, v, i, j = key.e1.v1, key.e1.v2, key.e2.v1, key.e2.v2
            path = h.path((i, j)).path
            for n_index in range(len(path) - 1):
                p1 = path[n_index]
                p2 = path[n_index + 1]
                weight = h.path((p1, p2)).length
                if self.prime_graph.has_edge(p1, p2):
                    self.prime_graph[p1][p2]["weight"] *= 10
                elif p1 != p2:
                    h_prime_length += weight
                self.prime_graph.add_edge(p1, p2, weight=weight)

        self.coverage = h_prime_length / h.total_length
