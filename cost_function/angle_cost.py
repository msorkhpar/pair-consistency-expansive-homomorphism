import math


def _vectors_angle(u, v, i, j):
    vector1 = (v[0] - u[0], v[1] - u[1])
    vector2 = (j[0] - i[0], j[1] - i[1])

    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    length_product = math.dist(u, v) * math.dist(i, j)
    return math.degrees(math.acos(dot_product / length_product))


def angle_cost(beta, u, v, i, j):
    theta = _vectors_angle(u, v, i, j)
    return beta * ((theta / 180) + (1 / beta))
