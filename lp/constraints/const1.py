import logging

from lp.parameters import Parameters

logger = logging.getLogger(__name__)


def const1(parameters: Parameters):
    for uv in parameters.g_edges:
        constraint = parameters.add_range_constraint(1, 1, f"sum of edge {uv} in G to edges in H == 1")
        string = ""
        for ij in parameters.h_edges:
            constraint.SetCoefficient(parameters.variable(uv, ij), 1)
            string += f"{parameters.variable(uv, ij)} + "

        logger.debug(f"{string[:-2]} = 1")
