import math

from lp.parameters import Parameters


def minimize_cost(parameter: Parameters):
    for mapping, variable in parameter.variables.items():
        cost = parameter.costs[mapping].cost
        parameter.set_objective_coefficient(variable, cost)
    parameter.minimization()
