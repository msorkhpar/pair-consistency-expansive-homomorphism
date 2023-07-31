from __future__ import annotations

import logging
import math
import sys
from functools import lru_cache

import networkx as nx
import numpy as np
from ortools.linear_solver import pywraplp

from utils.config import Config

logger = logging.getLogger(__name__)


class Edge:
    def __init__(self, vertex_tuple: tuple[tuple[int, int], tuple[int, int]]):
        v1, v2 = vertex_tuple
        self.v1: tuple[int, int] = v1
        self.v2: tuple[int, int] = v2

    def __str__(self):
        return f"[{self.v1}|{self.v2}]"

    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        return self.v1 == other.v1 and self.v2 == other.v2

    def __hash__(self):
        return hash((self.v1, self.v2))

    @staticmethod
    def from_index(index: str) -> Edge:
        u, v = index[1:-1].split("|")
        u = u[1:-1].split(",")
        u = (int(u[0]), int(u[1]))
        v = v[1:-1].split(",")
        v = (int(v[0]), int(v[1]))
        return Edge((u, v))


class EdgeMap:
    def __init__(self, e1: Edge | tuple[tuple[int, int], tuple[int, int]],
                 e2: Edge | tuple[tuple[int, int], tuple[int, int]]):
        if isinstance(e1, tuple):
            self.e1 = Edge(e1)
        else:
            self.e1 = e1
        if isinstance(e2, tuple):
            self.e1 = Edge(e2)
        else:
            self.e2 = e2

    def __str__(self):
        return f"[{self.e1}->{self.e2}]"

    def __eq__(self, other):
        if not isinstance(other, EdgeMap):
            return False
        return self.e1 == other.e1 and self.e2 == other.e2

    def __hash__(self):
        return hash((self.e1, self.e2))

    @staticmethod
    def from_index(index: str) -> EdgeMap:
        e1, e2 = index[1:-1].split("->")
        return EdgeMap(Edge.from_index(e1), Edge.from_index(e2))


class Parameters:
    def __init__(self, g: nx.Graph, h: nx.gnr_graph, g_edges: list[Edge], h_edges: list[Edge],
                 mapping_costs: dict[EdgeMap, dict[str, float]]):
        self.variables: dict[EdgeMap, pywraplp.Variable] = dict()
        self.g = g
        self.h = h
        self.g_edges = g_edges
        self.h_edges = h_edges
        self.mapping_costs = mapping_costs
        self._solver: pywraplp.Solver = pywraplp.Solver.CreateSolver(Config().solver_engine)
        self._objective: pywraplp.Objective = self._solver.Objective()

    def infinity(self) -> float:
        return self._solver.Infinity()

    def variable(self, e1: Edge, e2: Edge) -> pywraplp.Variable | None:
        mapping = EdgeMap(e1, e2)
        if mapping not in self.variables:
            return None
        return self.variables[mapping]

    def constraints_num(self) -> int:
        return self._solver.NumConstraints()

    def change_to_integral(self):
        [self.variables[key].SetInteger(True) for key in self.variables]

    def variables_num(self) -> int:
        return self._solver.NumVariables()

    def add_variable(self, e1: Edge, e2: Edge, lower_bound: float = 0.0, upper_bound: float = 1.0):
        mapping = EdgeMap(e1, e2)
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

    def solve(self) -> int:
        return self._solver.Solve()

    def objective_value(self) -> float:
        return self._objective.Value()

    def clear_context(self):
        self._solver.Clear()
