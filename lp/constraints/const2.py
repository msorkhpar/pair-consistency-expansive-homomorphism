import logging

from lp.parameters import Parameters, Edge

logger = logging.getLogger(__name__)


def __check_constraint_rule(parameters: Parameters, uv: Edge):
    u, v = uv
    for w in parameters.g.neighbors(u):
        if w != v:
            uw = Edge((u, w))
            for ij in parameters.h_edge_pairs:
                for st in parameters.h_edge_pairs:
                    pass
                    # if ij.v1 != st.v1:
                    #     parameters.add_constraint_rule(
                    #         parameters.variable(uv, ij) + parameters.variable(uw, st) <= 1
                    #     )


def const2(parameters: Parameters):
    for edge in parameters.g.edges():
        __check_constraint_rule(parameters, edge)
