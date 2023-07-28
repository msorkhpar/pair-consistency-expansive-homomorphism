def direction_cost(delta, u, v, i, j):
    def direction(coordinate1, coordinate2):
        return 1 if coordinate1 < coordinate2 else 0 if coordinate1 == coordinate2 else -1

    left_right = 0 if direction(u[0], v[0]) == direction(i[0], j[0]) else 1
    up_down = 0 if direction(u[1], v[1]) == direction(i[1], j[1]) else 1
    return delta * (left_right + up_down + 1 / delta)
