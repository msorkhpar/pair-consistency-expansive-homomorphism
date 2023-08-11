import math

import numpy as np


# Step 2: Define the Probability Cost Function
def probability_cost_function(percentage_g, percentage_h, a=2):
    if percentage_h == 0:
        return 1
    if percentage_g / percentage_h > 1.1:
        a *= a + a * ((percentage_g / percentage_h) - 1.1)
    return np.exp(-a * (percentage_g - percentage_h) ** 2)


def length_cost(gamma, total_g_length, total_h_length, min_h_length, uv_length, ij_length, u, v, i, j):
    g_length = uv_length / total_g_length
    h_length = ij_length / total_h_length

    if i == j and ij_length == 0:
        probability = probability_cost_function(g_length, (min_h_length / total_h_length))
    else:
        probability = probability_cost_function(g_length, h_length)
    cost = 1 - probability
    return (1 + cost) ** gamma
