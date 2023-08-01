import math


def _vectors_angle(u, v, i, j):
    vector1 = (v[0] - u[0], v[1] - u[1])
    vector2 = (j[0] - i[0], j[1] - i[1])

    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    length_product = math.dist(u, v) * math.dist(i, j)
    if length_product == 0:
        return 0
    return math.degrees(math.acos(round(dot_product / length_product, 10)))


def angle_cost(beta, u, v, i, j):
    theta = _vectors_angle(u, v, i, j)
    return beta * ((theta / 180))
