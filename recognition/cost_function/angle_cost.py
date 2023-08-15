import math

from utils.mathematics import vectors_angle


def angle_cost(alpha, u, v, i, j):
    theta = vectors_angle(u, v, i, j)
    return (1 + abs(theta) / 180) ** alpha
