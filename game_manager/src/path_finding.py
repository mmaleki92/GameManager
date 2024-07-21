import networkx as nx
import random

G = nx.path_graph(5)

print(nx.shortest_path(G, source=0, target=4))
# [0, 1, 2, 3, 4]
G = nx.grid_2d_graph(10,10)

nx.draw(G,  with_labels = True)
edge_colors = [random.choice(['black', 'red'])  for edge in G.edges()]
nx.draw(G, with_labels = True, font_color = 'white', edge_color= edge_colors, node_shape = 's')
G[0, 0][0, 1]["weight"] = 10
nx.draw(G)

