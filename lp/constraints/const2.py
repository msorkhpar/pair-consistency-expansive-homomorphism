import logging

from lp.parameters import Parameters, NodePair

logger = logging.getLogger(__name__)


def __check_constraint_rule(parameters: Parameters, uv: NodePair):
    u, v = uv.v1, uv.v2
    for w in parameters.g_neighbors[v]:
        if w != u:
            vw = NodePair((v, w))
            for ij in parameters.h_paths:
                uv_ij = parameters.variable(uv, ij)
                for jt in [candidate for candidate in parameters.h_node_participation[ij.v1] if
                           candidate.v1 == ij.v2 and ij.v1 != candidate.v2]:
                    constraint = parameters.add_range_constraint(
                        0, 1, f"X{uv},{ij} & X{vw},{jt} Homomorphic constraint"
                    )
                    constraint.SetCoefficient(uv_ij, 1)
                    constraint.SetCoefficient(parameters.variable(vw, jt), 1)


def const2(parameters: Parameters):
    for edge in parameters.g_edges:
        __check_constraint_rule(parameters, edge)
