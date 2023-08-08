import math

from cost_function.length_cost import length_cost
from cost_function.angle_cost import angle_cost
from cost_function.distance_cost import distance_cost
from input_graphs.input_graph import InputGraph
from mappings.mapping import Mapping
from mappings.mapping_cost import MappingCost


class MapGtoH:
    def _max_possible_mapping_distance(self):
        max_distance = 0
        for uv in self.g.edges(directed=True):
            for ij in self.h.edges(directed=True, self_loop=True):
                distance = math.dist(uv.v1, ij.v1) + math.dist(uv.v2, ij.v2)
                if distance > max_distance:
                    max_distance = distance + 1
        return max_distance

    def _uv_to_ij_cost(self, u, v, uv_length, ij) -> MappingCost:
        i = ij.v1
        j = ij.v2
        angle = angle_cost(self.alpha, u, v, i, j)
        distance = distance_cost(self.beta, self.max_distance, self.g.aspect_ratio, self.h.aspect_ratio, u, v, i, j)
        length = length_cost(
            self.gamma, self.g.total_length, self.h.total_length, self.h.min_length, uv_length, ij.length, u, v, i, j
        )
        cost = (angle * distance * length)
        return MappingCost(cost, angle, distance, length)

    def __init__(self, base_graph: InputGraph, h: InputGraph, alpha: float, beta: float, gamma: float):
        self.g: InputGraph = base_graph
        self.h: InputGraph = h
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.max_distance = self._max_possible_mapping_distance()

    def calculate_mapping_costs(self) -> dict[Mapping, MappingCost]:
        costs = dict()
        for uv in self.g.edges(directed=True):
            uv_length = math.dist(uv.v1, uv.v2)
            for ij in self.h.paths():
                costs[Mapping(uv, ij)] = self._uv_to_ij_cost(uv.v1, uv.v2, uv_length, ij)
        return costs
