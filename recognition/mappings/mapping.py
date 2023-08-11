from __future__ import annotations

from recognition.mappings.node_pair import NodePair


class Mapping:
    def __init__(self, e1: NodePair | tuple[tuple[int, int], tuple[int, int]],
                 e2: NodePair | tuple[tuple[int, int], tuple[int, int]]):
        if isinstance(e1, tuple):
            self.e1 = NodePair(e1)
        else:
            self.e1 = e1
        if isinstance(e2, tuple):
            self.e1 = NodePair(e2)
        else:
            self.e2 = e2

    def __str__(self):
        return f"[{self.e1}->{self.e2}]"

    def __eq__(self, other):
        if not isinstance(other, Mapping):
            return False
        return self.e1 == other.e1 and self.e2 == other.e2

    def __hash__(self):
        return hash((self.e1, self.e2))
