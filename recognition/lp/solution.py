from __future__ import annotations

from recognition.lp.parameters import Parameters
import logging

from recognition.mappings.mapping import Mapping
from recognition.mappings.mapping_cost import MappingCost
from recognition.mappings.node_pair import NodePair

logger = logging.getLogger(__name__)


class Solution:

    def __init__(self):
        self.cost: float | None = None
        self.variables: dict[Mapping, MappingCost] = dict()
        self.running_time: float | None = None

    def __str__(self):
        return f''' Solution(
        cost: {self.cost}
        running_time: {self.running_time}
        variables: {self.variables}
        )'''

    def assign_solution(self, parameter: Parameters):
        variables = {variable: value.solution_value() for variable, value in
                     parameter.variables.items() if value.solution_value() != 0}
        variables = dict(sorted(variables.items(), key=lambda x: x[1], reverse=True))
        mappings = {}
        for key in variables.keys():
            u, v, i, j = key.e1.v1, key.e1.v2, key.e2.v1, key.e2.v2
            dual_key = Mapping(NodePair((v, u)), NodePair((j, i)))
            if mappings.get(dual_key) is None:
                mappings[key] = parameter.costs[key]
        self.variables = mappings
        self.cost = parameter.objective_value() - len(parameter.g_edges)
