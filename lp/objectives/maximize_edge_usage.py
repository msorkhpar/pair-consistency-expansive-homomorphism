# import math
#
# from lp.parameters import Parameters
#
#
# def maximize_edge_usage(parameter: Parameters):
#     for edgeMapping, variable in parameter.variables.items():
#         if edgeMapping.e2.v1 == edgeMapping.e2.v2:
#             continue
#         parameter.set_objective_coefficient(variable, 1, "second")
#     parameter.maximization("second")
