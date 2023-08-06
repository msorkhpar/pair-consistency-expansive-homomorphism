import logging

from lp.parameters import Parameters, NodePair

logger = logging.getLogger(__name__)


def const0(parameters: Parameters):
    for uv in parameters.g_edges:
        vu = NodePair((uv.v2, uv.v1))
        for ij in parameters.h_paths:
            ji = NodePair((ij.v2, ij.v1))
            constraint = parameters.add_range_constraint(0, 0, f"{ij} - {ji} ==0")
            constraint.SetCoefficient(parameters.variable(uv, ij), 1)
            constraint.SetCoefficient(parameters.variable(vu, ji), -1)
