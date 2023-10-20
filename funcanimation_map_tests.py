import random

import osmnx as ox
from matplotlib import pyplot as plt

address = "Auf Der Wacht 31, Diez, Germany"
location = ox.geocode(address)
# map_graph = ox.graph_from_address(address, dist=200)


map_graph_directed = ox.graph_from_point(location, dist=1000, network_type="all")
map_graph = ox.utils_graph.get_undirected(map_graph_directed)
print("got street")

all_edges = list(map_graph.edges())
all_nodes = list(map_graph.nodes())

# Select two random nodes
random.seed(3)
random_nodes = random.choices(all_nodes, k=2)
source_node, target_node = random_nodes

node_size = 2
edge_linewidth = 1

node_color = 'g'
default_edge_color = 'r'

edge_colors = [default_edge_color] * len(all_edges)

fig, ax = ox.plot_graph(map_graph, node_size=node_size, node_color=node_color, edge_color=edge_colors,
                        edge_linewidth=edge_linewidth, show=False)

edge_colors = ['b'] * len(all_edges)
edge_colors[0] = 'r'
edge_colors[2] = 'r'
edge_colors[4] = 'r'
edge_colors[5] = 'r'


ax.collections[0].set_colors(edge_colors)




print(ax.collections[1])

plt.show()
