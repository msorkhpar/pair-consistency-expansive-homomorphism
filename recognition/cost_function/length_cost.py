from utils.mathematics import probability_cost_function


def length_cost(gamma, total_g_length, total_h_length, min_h_length, uv_length, ij_length, u, v, i, j):
    g_length = uv_length / total_g_length
    h_length = ij_length / total_h_length

    if i == j and ij_length == 0:
        probability = probability_cost_function(g_length, (min_h_length / total_h_length))
    else:
        probability = probability_cost_function(g_length, h_length)
    cost = 1 - probability
    return (1 + cost) ** gamma
