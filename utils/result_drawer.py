# from fractions import Fraction
#
# import networkx as nx
# import numpy as np
# import cv2
#
# from lp.parameters import EdgeMap
#
#
# def __draw_graph(output, graph: nx.Graph, x_padding=0, y_padding=0):
#     for u, v in graph.edges:
#         x1, y1 = u
#         x2, y2 = v
#
#         x1 = (x1 + x_padding) //2
#         x2 = (x2 + x_padding) //2
#         y1 = (y1 + y_padding) //2
#         y2 = (y2 + y_padding) //2
#         cv2.line(output, (x1, y1), (x2, y2), (0, 0, 0), 1)
#
#     for x, y in graph.nodes:
#         cv2.circle(output, (x//2, y//2), 2, (0, 0, 255), -1)
#
#
# def __drawline(img, pt1, pt2, color, thickness=1, style='dotted', gap=10):
#     dist = ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** .5
#     pts = []
#     for i in np.arange(0, dist, gap):
#         r = i / dist
#         x = int((pt1[0] * (1 - r) + pt2[0] * r) + .5)
#         y = int((pt1[1] * (1 - r) + pt2[1] * r) + .5)
#         p = (x//2, y//2)
#         pts.append(p)
#
#     if style == 'dotted':
#         for p in pts:
#             cv2.circle(img, p, thickness, color, -1)
#     else:
#         s = pts[0]
#         e = pts[0]
#         i = 0
#         for p in pts:
#             s = e
#             e = p
#             if i % 2 == 1:
#                 cv2.line(img, s, e, color, thickness)
#             i += 1
#
#
# def transport_to_cartesian(column, row, width, height):
#     x = column - (width / 2)
#     y = -(row - (height / 2))
#     return x, y
#
#
# def transport_to_pixel(x, y, width, height):
#     column = x + (width / 2)
#     row = -(y - (height / 2))
#     return int(column), int(row)
#
#
# def __draw_mapping(output, mappings: list[EdgeMap], x_padding=0, y_padding=0):
#     for mapping in mappings:
#         uv = mapping.e1
#         ij = mapping.e2
#
#         u_x, u_y = uv.v1
#         v_x, v_y = uv.v2
#         center_uv_x = (u_x + v_x) // 2
#         center_uv_y = (u_y + v_y) // 2
#
#         i_x, i_y = ij.v1
#         j_x, j_y = ij.v2
#         center_ij_x = (i_x + j_x) // 2
#         center_ij_y = (i_y + j_y) // 2
#
#         i_x += x_padding
#         j_x += x_padding
#         u_y += y_padding
#         v_y += y_padding
#         i_y += y_padding
#         j_y += y_padding
#         center_uv_x += x_padding
#         center_uv_y += y_padding
#         center_ij_x += x_padding
#         center_ij_y += y_padding
#
#         #__drawline(output, (u_x, u_y), (i_x, i_y), (0, 0, 0), 1, gap=35)
#         #__drawline(output, (v_x, v_y), (j_x, j_y), (0, 0, 0), 1,gap=35)
#         __drawline(output, (center_uv_x, center_uv_y), (center_ij_x, center_ij_y), (0, 0, 0), 1)
#
#
# def draw_LP_result(G: nx.Graph, H: nx.Graph, output_path: str,
#                    g_to_h_mappings: list[EdgeMap], h_to_g_mappings: list[EdgeMap] = None):
#     if not h_to_g_mappings:
#         main_output = np.ones((512, 512, 3), np.uint8) * 255
#         second_output = np.ones((512, 512, 3), np.uint8) * 255
#     else:
#         main_output = np.ones((2148, 512, 3), np.uint8) * 255
#         second_output = np.ones((2148, 512, 3), np.uint8) * 255
#
#     __draw_graph(main_output, G, 0, 0)
#     __draw_graph(second_output, H, 0, 0)
#     __draw_mapping(main_output, g_to_h_mappings, 0, 0)
#
#     if h_to_g_mappings:
#         __draw_graph(main_output, H, 0, 1124)
#         __draw_graph(second_output, G, 0, 1124)
#         __draw_mapping(main_output, h_to_g_mappings, 0, 1124)
#     output = cv2.addWeighted(main_output, 0.7, second_output, 0.3, 0)
#
#     if output_path:
#         cv2.imwrite(output_path, output)
#     else:
#         cv2.imshow("Graph.png", output)
#         cv2.waitKey(0)


from fractions import Fraction

import networkx as nx
import numpy as np
import cv2

from lp.parameters import EdgeMap, Edge


def __draw_graph(output, graph: nx.Graph, names: dict[tuple[int, int], str], x_padding=0, y_padding=0):
    for u, v in graph.edges():
        x1, y1 = u
        x2, y2 = v

        x1 = (x1 + x_padding)
        x2 = (x2 + x_padding)
        y1 = (y1 + y_padding)
        y2 = (y2 + y_padding)
        cv2.line(output, (x1, y1), (x2, y2), (0, 0, 0), 2)

    for x, y in graph.nodes:
        cv2.circle(output, (x, y), 3, (0, 0, 255), -1)
        p_x = (15 if x < 1024 / 3 else -20) + x
        p_y = (22 if y < 1024 / 2 else -15) + y
        cv2.putText(output, names[(x, y)], (p_x + x_padding, p_y + y_padding), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0),
                    2, cv2.LINE_AA, False)


def __drawline(img, pt1, pt2, color, thickness=1, style='dotted', gap=10):
    dist = ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** .5
    pts = []
    for i in np.arange(0, dist, gap):
        r = i / dist
        x = int((pt1[0] * (1 - r) + pt2[0] * r) + .5)
        y = int((pt1[1] * (1 - r) + pt2[1] * r) + .5)
        p = (x, y)
        pts.append(p)

    if style == 'dotted':
        for p in pts:
            cv2.circle(img, p, thickness, color, -1)
    else:
        s = pts[0]
        e = pts[0]
        i = 0
        for p in pts:
            s = e
            e = p
            if i % 2 == 1:
                cv2.line(img, s, e, color, thickness)
            i += 1


def __draw_mapping(output, mappings: dict[EdgeMap, dict[str, float]], names: dict[tuple[int, int], str], x_padding=0,
                   y_padding=0):
    counter = 1
    total_cost = 0
    for mapping, costs in mappings.items():
        uv = mapping.e1
        ij = mapping.e2

        u_x, u_y = uv.v1
        v_x, v_y = uv.v2
        center_uv_x = (u_x + v_x) // 2
        center_uv_y = (u_y + v_y) // 2

        i_x, i_y = ij.v1
        j_x, j_y = ij.v2
        center_ij_x = (i_x + j_x) // 2
        center_ij_y = (i_y + j_y) // 2

        i_x += x_padding
        j_x += x_padding
        u_y += y_padding
        v_y += y_padding
        i_y += y_padding
        j_y += y_padding
        center_uv_x += x_padding
        center_uv_y += y_padding
        center_ij_x += x_padding
        center_ij_y += y_padding

        # __drawline(output, (u_x, u_y), (i_x, i_y), (0, 0, 0), 1, gap=35)
        # __drawline(output, (v_x, v_y), (j_x, j_y), (0, 0, 0), 1, gap=35)
        __drawline(output, (center_uv_x, center_uv_y), (center_ij_x, center_ij_y), (0, 0, 0), 1)
        text = (
            f"{names[uv.v1]}{names[uv.v2]}->{names[ij.v1]}{names[ij.v2]}= {round(mappings[mapping]['cost'], 2)}  "
            f"[L={round(mappings[mapping]['length'], 2)}, A={round(mappings[mapping]['angle'], 2)},"
            f" Z={round(mappings[mapping]['distance'], 2)}, D={round(mappings[mapping]['direction'], 2)}, "
            f"O={round(mappings[mapping]['orientation'], 2)}]")
        total_cost += mappings[mapping]['cost']
        cv2.putText(output, text, (1050, 30 + counter * 50 + y_padding), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0),
                    2, cv2.LINE_AA, False)
        counter += 1
    cv2.putText(output, f"Total Cost= {round(total_cost, 3)}", (1050, 30 + y_padding), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                (0, 0, 0), 2, cv2.LINE_AA, False)


def _assign_name_to_node(names, counter, node):
    if node not in names:
        names[node] = chr(counter)
        counter += 1
    return counter


def __assign_names_to_nodes(names, counter, graph: nx.Graph):
    for node in graph.nodes:
        counter = _assign_name_to_node(names, counter, node)
    return counter


def draw_LP_result(G: nx.Graph, H: nx.Graph, output_path: str,
                   g_to_h_mappings: dict[EdgeMap, dict[str, float]],
                   h_to_g_mappings: dict[EdgeMap, dict[str, float]] = None):
    counter = 97
    names = {}
    counter = __assign_names_to_nodes(names, counter, G)
    counter = __assign_names_to_nodes(names, counter, H)

    if not h_to_g_mappings:
        main_output = np.ones((1024, 1024 + 900, 3), np.uint8) * 255
        second_output = np.ones((1024, 1024 + 900, 3), np.uint8) * 255
    else:
        main_output = np.ones((2148, 1024 + 900, 3), np.uint8) * 255
        second_output = np.ones((2148, 1024 + 900, 3), np.uint8) * 255

    __draw_graph(main_output, G, names, 0, 0)
    __draw_graph(second_output, H, names, 0, 0)
    __draw_mapping(second_output, g_to_h_mappings, names, 0, 0)

    if h_to_g_mappings:
        __draw_graph(main_output, G, names, 0, 1124)
        __draw_graph(second_output, H, names, 0, 1124)
        __draw_mapping(second_output, h_to_g_mappings, names, 0, 1124)

    output = cv2.addWeighted(main_output, 0.25, second_output, 0.75, 0)
    output = cv2.copyMakeBorder(output.copy(), 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])

    if output_path:
        cv2.imwrite(output_path, output)
    else:
        cv2.imshow("Graph.png", output)
        cv2.waitKey(0)
