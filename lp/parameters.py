from __future__ import annotations

import logging
from ortools.linear_solver import pywraplp

from input_graphs.input_graph import InputGraph
from mappings.mapping import Mapping
from mappings.mapping_cost import MappingCost
from mappings.node_pair import NodePair
from utils.config import Config

logger = logging.getLogger(__name__)


class Parameters:
    def __init__(self, g: InputGraph, h: InputGraph, costs: dict[Mapping, MappingCost]):
        self.variables: dict[Mapping, pywraplp.Variable] = dict()
        self.g_neighbors: dict[tuple[int, int], list[tuple[int, int]]] = g.neighbors()
        self.g_edges: list[NodePair] = g.edges(directed=True)
        self.h_paths: set[NodePair] = h.paths()
        self.h_node_participation: dict[tuple[int, int], set[NodePair]] = h.node_participation()
        self.costs: dict[Mapping, MappingCost] = costs
        self._solver: pywraplp.Solver = pywraplp.Solver.CreateSolver(Config().solver_engine)
        self._objective: pywraplp.Objective = self._solver.Objective()

    def infinity(self) -> float:
        return self._solver.Infinity()

    def variable(self, e1: NodePair, e2: NodePair) -> pywraplp.Variable | None:
        mapping = Mapping(e1, e2)
        if mapping not in self.variables:
            return None
        return self.variables[mapping]

    def constraints_num(self) -> int:
        return self._solver.NumConstraints()

    def change_to_integral(self):
        [self.variables[key].SetInteger(True) for key in self.variables]

    def variables_num(self) -> int:
        return self._solver.NumVariables()

    def add_variable(self, e1: NodePair, e2: NodePair, lower_bound: float = 0.0, upper_bound: float = 1.0):
        mapping = Mapping(e1, e2)
        self.variables[mapping] = self._solver.NumVar(lower_bound, upper_bound, mapping.__str__())

    def add_range_constraint(self, lower_bound: float, upper_bound: float, name=''):
        return self._solver.Constraint(
            lower_bound,
            upper_bound,
            name
        )

    def add_constraint_rule(self, constraint_rule: pywraplp.LinearConstraint):
        self._solver.Add(constraint_rule)

    def set_objective_coefficient(self, variable: pywraplp.Variable, coefficient: float):
        self._objective.SetCoefficient(variable, coefficient)

    def minimization(self):
        self._objective.SetMinimization()

    def maximization(self):
        self._objective.SetMaximization()

    def solve(self) -> int:
        return self._solver.Solve()

    def objective_value(self) -> float:
        return self._objective.Value()

    def clear_context(self):
        self._solver.Clear()
