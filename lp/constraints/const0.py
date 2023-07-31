import logging

from lp.parameters import Parameters, Edge

logger = logging.getLogger(__name__)


def __check_constraint_rule(parameters: Parameters, e1: Edge, u, v):
    for w in parameters.g.neighbors(v):
        if w != u:
            intermediate = Edge((v, w))
            if intermediate not in parameters.g_edges:
                intermediate = Edge((v, u))
            for ij in parameters.h_edges:
                for st in parameters.h_edges:
                    if ij.v1 != st.v1:
                        parameters.add_constraint_rule(
                            parameters.variable(e1, ij) + parameters.variable(intermediate, st) <= 1
                        )


def const0(parameters: Parameters):
    for uv in parameters.g_edges:
        vu = Edge((uv.v2, uv.v1))

        for ij in parameters.h_edges:
            ji = Edge((ij.v2, ij.v1))
            parameters.add_constraint_rule(
                parameters.variable(uv, ij) - parameters.variable(vu, ji) == 0
            )
