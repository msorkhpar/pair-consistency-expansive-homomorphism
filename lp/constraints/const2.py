import logging

from lp.parameters import Parameters, NodePair

logger = logging.getLogger(__name__)


def __check_constraint_rule(parameters: Parameters, uv: NodePair):
    u, v = uv.v1, uv.v2
    for w in parameters.g_neighbors[u]:
        if w != v:
            uw = NodePair((u, w))
            for ij in parameters.h_paths:
                uv_ij = parameters.variable(uv, ij)
                for st in parameters.h_paths:
                    if ij.v1 != st.v1:
                        constraint = parameters.add_range_constraint(0, 1, f"{ij}&{st} Homomorphic constraint")
                        constraint.SetCoefficient(uv_ij, 1)
                        constraint.SetCoefficient(parameters.variable(uw, st), 1)


def const2(parameters: Parameters):
    for edge in parameters.g_edges:
        __check_constraint_rule(parameters, edge)
