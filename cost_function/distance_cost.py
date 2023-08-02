import math


def distance_cost(alpha, max_distance, u, v, i, j):
    return alpha * (math.dist(u, i) + math.dist(v, j)) / max_distance
