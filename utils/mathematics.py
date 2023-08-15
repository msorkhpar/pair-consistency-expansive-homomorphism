import math

import numpy as np


def distance_from_path_percentage(u, v, w):
    w = np.array(w)
    u = np.array(u)
    v = np.array(v)
    line_vector = v - u
    point_vector = w - u

    distance = np.linalg.norm(np.cross(line_vector, point_vector)) / np.linalg.norm(line_vector)
    line_length = math.dist(u, v)
    return (distance / line_length) * 100


def vectors_angle(u, v, i, j):
    vector1 = (v[0] - u[0], v[1] - u[1])
    vector2 = (j[0] - i[0], j[1] - i[1])

    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    length_product = math.dist(u, v) * math.dist(i, j)
    if length_product == 0:
        return 0
    return math.degrees(math.acos(round(dot_product / length_product, 10)))


def probability_cost_function(percentage_g, percentage_h, a=2):
    if percentage_h == 0:
        return 1
    if percentage_g / percentage_h > 1.1:
        a *= a + a * ((percentage_g / percentage_h) - 1.1)
    return np.exp(-a * (percentage_g - percentage_h) ** 2)
