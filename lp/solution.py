from __future__ import annotations

from lp.parameters import Parameters, EdgeMap, NodePair
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
        self.cost = parameter.objective_value() - len(parameter.g_edges)
