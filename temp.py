import networkx as nx

# Create an undirected graph
G = nx.DiGraph()

# Add edge (u, v)
G.add_edge('u', 'v')

# Manually add edge (v, u) as well
G.add_edge('v', 'u')

# Access the list of edges
edge_list = list(G.edges())

print(edge_list)
