import logging

from recognition.input_graph import InputGraph
from recognition.lp.solver import Solver
from recognition.mappings import mapper
from recognition.mappings.h_prime_builder import HPrime
from utils.config import Config

config = Config()
logger = logging.getLogger(__name__)


def compare(base_graph: InputGraph, target_graph: InputGraph):
    costs = mapper.MapGtoH(base_graph, target_graph, config.alpha, config.beta, config.gamma).calculate_mapping_costs()
    solution = Solver(base_graph, target_graph, costs).solve()
    if solution is None:
        return costs, None, None
    target_prime = HPrime(target_graph, solution)
    return costs, solution, target_prime


def calculate_cost(g: InputGraph, h: InputGraph) -> tuple[float, float, float]:
    _, g_to_h_solution, h_prime = compare(g, h)
    _, h_to_g_solution, g_prime = compare(h, g)
    if g_to_h_solution is None:
        g_h_cost = -1
    else:
        g_h_cost = g_to_h_solution.cost
    if h_to_g_solution is None:
        h_g_cost = -1
    else:
        h_g_cost = h_to_g_solution.cost

    if h_g_cost != -1 and g_h_cost != -1:
        cost = h_g_cost + h_g_cost * (1 - g_prime.coverage)
        cost += g_h_cost + g_h_cost * (1 - h_prime.coverage)
        return g_h_cost, h_g_cost, cost

    return g_h_cost, h_g_cost, -1

def calculate_cost_concurrently(args):
    subject_graph, base_graph = args
    subject_to_base_cost, base_to_subject_cost, cost = calculate_cost(subject_graph, base_graph)
    result = {
        "base_graph_name": base_graph.name,
        "g_to_h_cost": subject_to_base_cost,
        "h_to_g_cost": base_to_subject_cost,
        "detected": base_graph.digit == subject_graph.digit,
        "cost": cost
    }
    return result
