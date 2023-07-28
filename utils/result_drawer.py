import networkx as nx
import numpy as np
import cv2

from lp.parameters import EdgeMap


def __draw_graph(output, graph: nx.Graph, x_padding=0, y_padding=0):
    for u, v in graph.edges:
        x1, y1 = u
        x2, y2 = v
        cv2.line(output, (x1 + x_padding, y1 + y_padding), (x2 + x_padding, y2 + y_padding), (0, 0, 0), 1)

    for x, y in graph.nodes:
        cv2.circle(output, (x + x_padding, y + y_padding), 2, (0, 0, 255), -1)


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


def transport_to_cartesian(column, row, width, height):
    x = column - (width / 2)
    y = -(row - (height / 2))
    return x, y


def __draw_mapping(output, mappings: list[EdgeMap]):
    for mapping in mappings:
        uv = mapping.e1
        ij = mapping.e2
        u_x, u_y = uv.v1
        v_x, v_y = uv.v2
        center_uv_x = (u_x + v_x) // 2
        center_uv_y = (u_y + v_y) // 2
        i_x, i_y = ij.v1
        j_x, j_y = ij.v2

        center_ij_x = (i_x + j_x) // 2
        center_ij_y = (u_y + j_y) // 2
        __drawline(output, (center_uv_x, center_uv_y), (center_ij_x, center_ij_y), (0, 0, 0), 1)


def draw_LP_result(G: nx.Graph, H: nx.Graph, output_path: str,
                   g_to_h_mappings: list[EdgeMap]):
    main_output = np.ones((1024, 1024, 3), np.uint8) * 255
    second_output = np.ones((1024, 1024, 3), np.uint8) * 255

    __draw_graph(main_output, G, 0, 0)
    __draw_graph(second_output, H, 0, 0)
    __draw_mapping(main_output, g_to_h_mappings)

    output = cv2.addWeighted(main_output, 0.7, second_output, 0.3, 0)

    if output_path:
        cv2.imwrite(output_path, output)
    else:
        cv2.imshow("Graph.png", output)
        cv2.waitKey(0)
