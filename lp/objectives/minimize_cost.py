import math

from lp.parameters import Parameters


def minimize_cost(parameter: Parameters):
    parameter.model.Minimize(
        sum(parameter.costs[mapping].cost * variable for mapping, variable in parameter.variables.items())
    )
