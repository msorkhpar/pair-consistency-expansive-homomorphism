import math

from lp.parameters import Parameters


def minimize_distance(parameter: Parameters):
    for edgeMapping, variable in parameter.variables.items():
        cost = parameter.mapping_costs[edgeMapping]["cost"]
        parameter.set_objective_coefficient(variable, cost)
    parameter.minimization()
