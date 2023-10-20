import heapq
import math
import random

import networkx as nx
import osmnx as ox
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# colors
WHITE = "#FFFFFF"
BLACK = "#000000"
GREEN = "#4F9E52"
LGREEN = "#00FF00"
MAGENTA = "#FF00FF"
BLUE = "#0000FF"
RED = "#FF0000"
GRAY = "#7D7D7D"

DEFAULT = 0
SOURCE = 1
TARGET = 2
EXPLORING = 3
EXPLORED = 4
PATH = 5

colors = {
    DEFAULT: WHITE,
    SOURCE: MAGENTA,
    TARGET: BLUE,
    EXPLORING: LGREEN,
    EXPLORED: GREEN,
    PATH: RED
}

network_type = "drive"

address = 'Los Angeles, California'
radius = 2000

address = "Instituto Superior Técnico, Lisboa, Portugal"
radius = 1200

location = ox.geocode(address)
map_graph_directed = ox.graph_from_point(location, dist=radius, network_type=network_type)

# map_graph_directed = ox.graph_from_address('Maputo, Mozambique')

map_graph = ox.utils_graph.get_undirected(map_graph_directed)


map_graph = nx.to_undirected(map_graph_directed)

print("Converted to undirected graph.")

all_nodes = list(map_graph.nodes())
all_edges = list(map_graph.edges())
edge_set = set()  # ensures that (u,v) or (v,u) is the same when checking.
for edge in all_edges:
    edge_set.add(edge)

# Select two random nodes
random.seed(0)
random_nodes = random.choices(all_nodes, k=2)
source_node, target_node = random_nodes

# Get the two nodes at the corners
nodes, _ = ox.graph_to_gdfs(map_graph)
min_lat, min_lon, max_lat, max_lon = nodes['y'].min(), nodes['x'].min(), nodes['y'].max(), nodes['x'].max()
corner_nodes = ox.distance.nearest_nodes(map_graph, (min_lat, min_lon), (max_lat, max_lon))
source_node, target_node = corner_nodes

print(f"Source node: {source_node}")
print(f"Target node: {target_node}")

# node_size = 10
# edge_linewidth = 1

node_size = 5
edge_linewidth = 0.5

edge_colors = [colors[DEFAULT]] * len(all_edges)
node_colors = [colors[DEFAULT]] * len(all_nodes)

for i in range(len(all_nodes)):
    if all_nodes[i] == source_node:
        node_colors[i] = colors[SOURCE]
    elif all_nodes[i] == target_node:
        node_colors[i] = colors[TARGET]

fig, ax = ox.plot_graph(map_graph, node_size=node_size, edge_linewidth=edge_linewidth,
                        node_color=node_colors, edge_color=edge_colors, show=False)

plot_lc = ax.collections[0]  # plot LineCollection

plotting_only = False
if plotting_only:
    plt.show()
    exit(0)

# DIJKSTRA
found_solution = False

queue = [(0, source_node)]  # create a priority queue

distances = {}  # distances
for n in all_nodes:
    distances[n] = math.inf
distances[source_node] = 0

visited = set()  # set of visited nodes
path = []

pivot_node = None  # used to reconstruct the path only
total_distance = 0


def dijkstra(frame):
    global found_solution, pivot_node, total_distance

    # reconstruct path in each frame
    if found_solution:

        if pivot_node != source_node:
            neighbor_nodes = map_graph.neighbors(pivot_node)
            for neighbor in neighbor_nodes:
                if map_graph.has_edge(pivot_node, neighbor):  # some neighbors have no edge to them, god knows why
                    edge_data = map_graph.get_edge_data(pivot_node, neighbor)
                    first_key = next(iter(edge_data))  # key is 0 or a diff number, god knows why
                    distance = edge_data[first_key]['length']
                    if neighbor in visited and distances[neighbor] + distance == distances[pivot_node]:
                        total_distance += distance
                        path.append(neighbor)
                        pivot_node = neighbor
        else:
            print(f"Done. dist: {total_distance} path:\n {path}")

        for i in range(len(path) - 1):
            # color the path
            nodeA = path[i]
            nodeB = path[i + 1]

            for k, edge_tup in enumerate(all_edges):
                if edge_tup == (nodeA, nodeB) or edge_tup == (nodeB, nodeA):
                    edge_index = k
                    break

            edge_colors[edge_index] = colors[PATH]
            plot_lc.set_colors(edge_colors)

        return

    if queue:
        current_distance, node = heapq.heappop(queue)  # Pop the node with the shortest distance
        if node in visited:
            return

        visited.add(node)

        # Check if the end node is reached
        if node == target_node:
            found_solution = True
            pivot_node = target_node

            path.append(target_node)
            return

        # explore node
        neighbor_nodes = map_graph.neighbors(node)
        for neighbor in neighbor_nodes:

            if map_graph.has_edge(node, neighbor):  # some neighbors have no edge to them, god knows why

                if neighbor not in visited:

                    edge_data = map_graph.get_edge_data(node, neighbor)
                    first_key = next(iter(edge_data))  # key is 0 or a diff number, god knows why
                    dist_to_neighbor = edge_data[first_key]['length']  # assuming there's only one edge between nodes

                    new_distance = current_distance + dist_to_neighbor
                    if new_distance < distances[neighbor]:
                        # color neighbor node as being explored

                        for k, edge_tup in enumerate(all_edges):
                            if edge_tup == (node, neighbor) or edge_tup == (neighbor, node):
                                edge_index = k
                                break
                        edge_colors[edge_index] = colors[EXPLORING]
                        plot_lc.set_colors(edge_colors)

                        distances[neighbor] = new_distance
                        heapq.heappush(queue, (new_distance, neighbor))

        # color node explored
        # node_index = all_nodes.index(node)
        # node_colors[node_index] = colors[EXPLORING]


ms_per_frame = 0  # animation speed
animation = FuncAnimation(fig, dijkstra, interval=ms_per_frame, blit=False, cache_frame_data=False)
plt.show()
