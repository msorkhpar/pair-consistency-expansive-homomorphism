import math


class NodePair:
    def __init__(self, vertex_tuple: tuple[tuple[int, int], tuple[int, int]], length: float = None, path=None):
        v1, v2 = vertex_tuple
        self.length = length
        self.path = path
        if length is None:
            self.length = math.dist(v1, v2)
        self.v1: tuple[int, int] = v1
        self.v2: tuple[int, int] = v2

    def __str__(self):
        return f"[{self.v1}|{self.v2}]"

    def __eq__(self, other):
        if not isinstance(other, NodePair):
            return False
        return self.v1 == other.v1 and self.v2 == other.v2

    def __hash__(self):
        return hash((self.v1, self.v2))
