import random
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

address = "Auf Der Wacht 31, Diez, Germany"
location = ox.geocode(address)
# map_graph = ox.graph_from_address(address, dist=200)


map_graph_directed = ox.graph_from_point(location, dist=1000, network_type="all")
map_graph = ox.utils_graph.get_undirected(map_graph_directed)
print("got street")

all_edges = list(map_graph.edges())

# Select two random nodes
random.seed(3)
random_nodes = random.choices(list(map_graph.nodes()), k=2)
source_node, target_node = random_nodes

# Get the two nodes at the corners
nodes, _ = ox.graph_to_gdfs(map_graph)
min_lat, min_lon, max_lat, max_lon = nodes['y'].min(), nodes['x'].min(), nodes['y'].max(), nodes['x'].max()
corner_nodes = ox.distance.nearest_nodes(map_graph, (min_lat, min_lon), (max_lat, max_lon))
source_node, target_node = corner_nodes

# Find the shortest path between the source and target nodes
shortest_path = nx.shortest_path(map_graph, source=source_node, target=target_node)
print(source_node, target_node)

# Create an initial list of edge colors, set all edges to 'w' (white)
all_edges = list(map_graph.edges())

node_size = 2
edge_linewidth = 1

node_color = 'g'
default_edge_color = 'r'
path_edge_color = 'b'

edge_colors = [default_edge_color] * len(all_edges)

n_frames = len(shortest_path) - 1
n_frames += 1

print(f"len shortest_path: {len(shortest_path)}")


def color_shortest_path():
    for i in range(len(shortest_path) - 1):
        u, v = shortest_path[i], shortest_path[i + 1]

        if (u, v) in all_edges:
            edge_index = all_edges.index((u, v))
        else:
            edge_index = all_edges.index((v, u))

        edge_colors[edge_index] = path_edge_color


print(edge_colors)

fig, ax = ox.plot_graph(map_graph, node_size=node_size, node_color=node_color, edge_color=edge_colors,
                        edge_linewidth=edge_linewidth, show=False)


def update(frame):
    # if last frame, reset colors
    if frame == n_frames - 1:
        for (u, v) in all_edges:
            edge_colors[all_edges.index((u, v))] = default_edge_color

    # else, update colors
    else:

        u, v = shortest_path[frame], shortest_path[frame + 1]

        if (u, v) in all_edges:
            edge_index = all_edges.index((u, v))
        else:
            edge_index = all_edges.index((v, u))

        edge_colors[edge_index] = path_edge_color

    # Clear the existing plot
    ax.cla()

    # Replot the graph with updated edge colors
    ox.plot_graph(map_graph, node_size=node_size, node_color=node_color, edge_color=edge_colors,
                  edge_linewidth=edge_linewidth, ax=ax, show=False)


ms_per_frame = 200  # animation speed
# blit maybe
animation = FuncAnimation(fig, update, frames=n_frames, repeat=True, interval=ms_per_frame)
plt.show()
