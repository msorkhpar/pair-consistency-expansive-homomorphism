import networkx as nx
import numpy as np
import cv2

from mapping import Mapping
from mapping_cost import MappingCost


class MappingDrawer:
    def _draw_graph(self, output, graph: nx.Graph, y_padding=0, color=(0, 0, 0)):
        for u, v in graph.edges():
            x1, y1 = u
            x2, y2 = v
            y1 = (y1 + y_padding)
            y2 = (y2 + y_padding)
            cv2.line(output, (x1, y1), (x2, y2), color, 2)
        for x, y in graph.nodes:
            cv2.circle(output, (x, y), 3, (0, 0, 255), -1)
            p_x = (15 if x < 1024 / 3 else -20) + x
            p_y = (22 if y < 1024 / 2 else -15) + y
            cv2.putText(output, self.labels[(x, y)], (p_x, p_y + y_padding), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                        (0, 0, 0),
                        2, cv2.LINE_AA, False)

    def _draw_mapping(self, output, mappings: dict[Mapping, MappingCost], y_padding=0):
        counter = 1
        total_cost = 0
        for mapping, costs in mappings.items():
            u, v = mapping.e1.v1, mapping.e1.v2
            i, j = mapping.e2.v1, mapping.e2.v2

            text = (
                f"{self.labels[u]}{self.labels[v]}->{self.labels[i]}{self.labels[j]}= "
                f"{round(mappings[mapping].cost, 2)}  "
                f"[D={round(mappings[mapping].distance, 2)}, "
                f"A={round(mappings[mapping].angle, 2)}, "
                f"L={round(mappings[mapping].length, 2)}]"
            )
            total_cost += mappings[mapping].cost
            cv2.putText(output, text, (1050, 30 + counter * 50 + y_padding), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0),
                        2, cv2.LINE_AA, False)
            counter += 1
        cv2.putText(output, f"Total Cost= {round(total_cost, 3)}", (1050, 30 + y_padding), cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 0), 2, cv2.LINE_AA, False)

    @staticmethod
    def _assign_name_to_node(labels, counter, node):
        if node not in labels:
            labels[node] = chr(counter)
            counter += 1
        return counter

    @staticmethod
    def _assign_names_to_nodes(labels, counter, graph: nx.Graph):
        for node in graph.nodes:
            counter = MappingDrawer._assign_name_to_node(labels, counter, node)
        return counter

    def _generate_node_labels(self):
        counter = 97
        labels = {}
        counter = MappingDrawer._assign_names_to_nodes(labels, counter, self.g)
        MappingDrawer._assign_names_to_nodes(labels, counter, self.h)
        return labels

    def _draw(self, output, second_output, base_graph, target_graph, prime_graph, mappings, y_padding=0):
        self._draw_graph(output, base_graph, y_padding=y_padding)
        self._draw_graph(second_output, target_graph, y_padding=y_padding)
        self._draw_graph(second_output, prime_graph, y_padding=y_padding, color=(0, 0, 255))
        self._draw_mapping(second_output, mappings, y_padding)

    def __init__(self, output_dir: str, g: nx.Graph, h: nx.Graph, h_prime: nx.Graph, g_to_h_mappings,
                 g_prime: nx.Graph = None, h_to_g_mappings=None):
        self.g = g
        self.h = h
        self.g_prime = g_prime
        self.h_prime = h_prime
        self.g_to_h_mappings = g_to_h_mappings
        self.h_to_g_mappings = h_to_g_mappings
        self.labels = self._generate_node_labels()
        self.output_dir = output_dir

    def draw(self):
        height = 1024
        if self.h_to_g_mappings:
            height = 2148
        main_output = np.ones((height, 1024 + 900, 3), np.uint8) * 255
        second_output = np.ones((height, 1024 + 900, 3), np.uint8) * 255
        self._draw(main_output, second_output, self.g, self.h, self.h_prime, self.g_to_h_mappings)
        if self.h_to_g_mappings:
            self._draw(main_output, second_output, self.h, self.g, self.g_prime, self.h_to_g_mappings, 1124)

        output = cv2.addWeighted(main_output, 0.25, second_output, 0.75, 0)
        output = cv2.copyMakeBorder(output.copy(), 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        cv2.imwrite(self.output_dir, output)
