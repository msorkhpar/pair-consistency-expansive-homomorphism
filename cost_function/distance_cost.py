import math


def distance_cost(gamma, max_distance, u, v, i, j):
    return gamma * (((math.dist(u, i) + math.dist(v, j)) / max_distance))
