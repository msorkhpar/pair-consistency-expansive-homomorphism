import math


def distance_cost(beta, max_distance, g_aspect_ratio, h_aspect_ratio, u, v, i, j):
    cost = 1 + (math.dist(u, i) + math.dist(v, j)) / max_distance * g_aspect_ratio / h_aspect_ratio
    if i == j:
        return cost ** beta ** 2
    return cost ** beta
