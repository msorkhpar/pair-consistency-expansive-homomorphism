import logging

from lp.parameters import Parameters, NodePair

logger = logging.getLogger(__name__)


def const0(parameters: Parameters):
    for uv in parameters.g_edges:
        vu = NodePair((uv.v2, uv.v1))

        for ij in parameters.h_edge_pairs:
            ji = NodePair((ij.v2, ij.v1))
            parameters.add_constraint_rule(
                parameters.variable(uv, ij) - parameters.variable(vu, ji) == 0
            )
