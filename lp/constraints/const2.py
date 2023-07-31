import logging

from lp.parameters import Parameters, Edge

logger = logging.getLogger(__name__)


def __check_constraint_rule(parameters: Parameters, e1: Edge, u, v):
    for w in parameters.g.neighbors(u):
        if w != v:
            intermediate = Edge((u, w))
            if intermediate not in parameters.g_edges:
                intermediate = Edge((w, u))
            for ij in parameters.h_edges:
                for st in parameters.h_edges:
                    if ij.v1 != st.v1:
                        parameters.add_constraint_rule(
                            parameters.variable(e1, ij) +
                            parameters.variable(intermediate, st) <= 1
                        )


def const2(parameters: Parameters):
    for edge in parameters.g.edges():
        u, v = edge
        __check_constraint_rule(parameters, edge, u, v)
        __check_constraint_rule(parameters, edge, v, u)
