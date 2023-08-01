from sympy import Point, Segment


def _segments_intersection(u, v, i, j):
    uv = Segment(Point(u[0], u[1]), Point(v[0], v[1]))
    ij = Segment(Point(i[0], i[1]), Point(j[0], j[1]))
    if u==v or i==j:
        return False

    t_ij = ij.perpendicular_bisector()
    return len(t_ij.intersection(uv)) > 0


def orientation_cost(tau, u, v, i, j):
    if _segments_intersection(u, v, i, j):
        return 1
    else:
        return tau * (1 + 1 / tau)
