import logging

from lp.parameters import Parameters

logger = logging.getLogger(__name__)


def create_edges_mapping_variables(parameters: Parameters):
    for uv in parameters.g_edges:
        for ij in parameters.h_edges:
            parameters.add_variable(uv, ij)
            logger.debug(f"0 =< {parameters.variable(uv, ij)} <= 1")
