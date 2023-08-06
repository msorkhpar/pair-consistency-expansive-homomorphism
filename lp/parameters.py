from __future__ import annotations

import logging
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model

from input_graph import InputGraph
from mapping import Mapping
from mapping_cost import MappingCost
from node_pair import NodePair
from utils.config import Config

logger = logging.getLogger(__name__)


class Parameters:
    def __init__(self, g: InputGraph, h: InputGraph, costs: dict[Mapping, MappingCost]):
        self.variables: dict[Mapping, cp_model.IntVar] = dict()
        self.g_neighbors: dict[tuple[int, int], list[tuple[int, int]]] = g.neighbors()
        self.g_edges: list[NodePair] = g.edges(directed=True)
        self.h_paths: set[NodePair] = h.paths()
        self.costs: dict[Mapping, MappingCost] = costs
        self.model: cp_model.CpModel = cp_model.CpModel()
        self.solver: cp_model.CpSolver = cp_model.CpSolver()

    def variable(self, e1: NodePair, e2: NodePair) -> cp_model.IntVar | None:
        mapping = Mapping(e1, e2)
        if mapping not in self.variables:
            return None
        return self.variables[mapping]

    def add_variable(self, e1: NodePair, e2: NodePair, lower_bound: int = 0, upper_bound: int = 1):
        mapping = Mapping(e1, e2)
        self.variables[mapping] = self.model.NewIntVar(lower_bound, upper_bound, mapping.__str__())

    def add_constraint_rule(self, constraint_rule):
        self.model.Add(constraint_rule)

    def solve(self) -> int:
        return self.solver.Solve(self.model)

    def objective_value(self) -> int:
        return self.solver.ObjectiveValue()
