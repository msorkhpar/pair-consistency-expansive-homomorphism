import logging

from lp.parameters import Parameters

logger = logging.getLogger(__name__)


def const1(parameters: Parameters):
    for uv in parameters.g_edges:
        parameters.add_constraint_rule(sum(parameters.variable(uv, ij) for ij in parameters.h_paths) == 1)
