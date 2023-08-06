from __future__ import annotations

import logging
import time

import networkx as nx
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model

from input_graph import InputGraph
from lp.parameters import Parameters
from lp.solution import Solution
from lp.variables.mapping_variables import create_edges_mapping_variables
from lp.constraints.const0 import const0
from lp.constraints.const1 import const1
from lp.constraints.const2 import const2
from lp.objectives.minimize_cost import minimize_cost
from mapping import Mapping
from mapping_cost import MappingCost
from utils.config import Config

logger = logging.getLogger(__name__)


class Solver:
    def _assign_name_to_node(self, names, counter, node):
        if node not in names:
            names[node] = chr(counter)
            counter += 1
        return counter

    def __assign_names_to_nodes(self, names, counter, graph: nx.Graph):
        for node in graph.nodes:
            counter = self._assign_name_to_node(names, counter, node)
        return counter

    def __init__(self, g: InputGraph, h: InputGraph, costs: dict[Mapping, MappingCost]):
        self.start = time.time()
        self.parameters = Parameters(g, h, costs)
        self._create_variables()
        self._set_up_constraints()
        self._set_objective()

    def _create_variables(self):
        logger.debug("Creating variables initiated")
        create_edges_mapping_variables(self.parameters)
        logger.debug("Creating variables finished")

    def _set_up_constraints(self):
        logger.debug("Setting up constraints initiated")
        const0(self.parameters)
        const1(self.parameters)
        const2(self.parameters)
        logger.debug("Setting up constraints finished")

    def _set_objective(self):
        logger.debug("Setting objective initiated")
        minimize_cost(self.parameters)
        logger.debug("Setting objective finished")

    def solve(self) -> Solution | None:
        try:
            logger.debug("Solving the problem initiated")
            status = self.parameters.solve()
            if status == cp_model.OPTIMAL:
                solution = Solution()
                solution.running_time = time.time() - self.start
                solution.assign_solution(self.parameters)
                return solution
            elif status == pywraplp.Solver.INFEASIBLE:
                logger.error("Given problem is infeasible")
            logger.debug("Solving process was not successful")
            return None
        finally:
            self.clear()

    def clear(self):
        del self.parameters
