import math


def distance_cost(alpha, max_distance, g_aspect_ratio, h_aspect_ratio, u, v, i, j):
    cost = 1 + (alpha * (math.dist(u, i) + math.dist(v, j)) / max_distance) * g_aspect_ratio / h_aspect_ratio
    if i == j:
        return cost ** 9
    return cost ** 3
