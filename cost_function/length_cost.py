import math


def length_cost(alpha, total_G_length, total_H_length, u, v, i, j):
    G_length = math.dist(u, v) / total_G_length
    H_length = math.dist(i, j) / total_H_length
    mu = G_length / H_length
    if G_length / H_length <= 1.1:
        return alpha
    else:
        return alpha * mu
