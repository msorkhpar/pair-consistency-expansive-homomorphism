from __future__ import annotations

from lp.parameters import Parameters, EdgeMap, Edge
import logging

logger = logging.getLogger(__name__)


class Solution:

    def __init__(self):
        self.cost: float | None = None
        self.variables: dict[EdgeMap, float] = dict()
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
        self.variables = variables.copy()
        self.cost = parameter.objective_value()

    def relabel_variables(self, g_labels, h_labels):
        result = {}
        for mapping, value in self.variables.items():
            uv = mapping.e1
            ij = mapping.e2
            new_mapping = EdgeMap(Edge((g_labels[uv.v1], g_labels[uv.v2])), Edge((h_labels[ij.v1], h_labels[ij.v2])))
            result[new_mapping] = value
        self.variables = result
