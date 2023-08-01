import networkx as nx
import numpy as np
from itertools import product

from utils.h_path_builder import build_degree_two_paths


# Step 1: Calculate Percentages
def calculate_percentages(graph):
    total_weight = sum([data['weight'] for _, _, data in graph.edges(data=True)])
    for u, v, data in graph.edges(data=True):
        data['percentage'] = data['weight'] / total_weight


# Step 2: Define the Probability Cost Function
def probability_cost_function(percentage_g, percentage_h, alpha=4):
    if percentage_h == 0:
        return 1
    if percentage_g / percentage_h > 1.1:
        alpha *= 2.5
    return np.exp(-alpha * (percentage_g - percentage_h) ** 2)


# Create Graph G and H (Replace this with your own graphs)
G = nx.Graph()
G.add_edge("u", "v", weight=68)
G.add_edge("v", "w", weight=7)
G.add_edge("w", "x", weight=25)

H = nx.Graph()
H.add_edge('i', 'j', weight=25)
H.add_edge('j', 'k', weight=40)
H.add_edge('k', 'l', weight=10)
H.add_edge('l', 'm', weight=25)

# Step 1: Calculate Percentages for Graph G and H
calculate_percentages(G)
calculate_percentages(H)

# Step 2: Create a dictionary with permutation pairs and their probabilities
edge_probabilities = {}

h_paths = build_degree_two_paths(H)
for (u_g, v_g), (u_h, v_h) in product(G.edges(), h_paths.keys()):

    percentage_g = (G[u_g][v_g]['percentage'])
    if u_h == v_h:
        percentage_h = 0.025
    else:
        percentage_h = h_paths[(u_h, v_h)] / 100

    probability = probability_cost_function(percentage_g, percentage_h)
    edge_probabilities[(u_g, v_g, u_h, v_h)] = probability

# Sort the dictionary based on probabilities in descending order
sorted_edge_penalties = {k: round(100 - 100 * v,3) for k, v in
                             sorted(edge_probabilities.items(), key=lambda item: item[1], reverse=False)}

# Print the dictionary with permutations and probabilities
for edges, penalty in sorted_edge_penalties.items():
    u_g, v_g, u_h, v_h = edges
    print(f"Edge ({u_g}, {v_g}) in G matches edge ({u_h}, {v_h}) in H with penalty [{penalty}]")
