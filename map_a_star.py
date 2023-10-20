import heapq
import math
import random

import osmnx as ox
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from geopy.distance import great_circle  # for calculating dist only

# colors
WHITE = "#FFFFFF"
BLACK = "#000000"
ORANGE = '#FF6C00'
LORANGE = '#E6965C'
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
    EXPLORING: LORANGE,
    EXPLORED: ORANGE,
    PATH: RED
}

network_type = "drive"
address = "Instituto Superior Técnico, Lisboa, Portugal"
radius = 1200

address = 'Los Altos, California, USA'
radius = 5000

address = 'Modena, Italy'
radius = 10000

address = 'Los Angeles, California'
radius = 5000

address = "Universidade de Aveiro, Aveiro, Portugal"
radius = 1500

address = "Matosinhos, Portugal"
radius = 1400

node_size = 2
edge_linewidth = 0.5

location = ox.geocode(address)
map_graph_directed = ox.graph_from_point(location, dist=radius, network_type=network_type)

map_graph = ox.utils_graph.get_undirected(map_graph_directed)
print("Converted to undirected graph.")

graph_nodes_with_data = map_graph.nodes(data=True)

all_edges = list(map_graph.edges())
all_nodes = list(map_graph.nodes())

# Select two random nodes
random.seed(0)
random_nodes = random.choices(all_nodes, k=2)
source_node, target_node = random_nodes

# Get the two nodes at the corners
nodes, _ = ox.graph_to_gdfs(map_graph)
min_lat, min_lon, max_lat, max_lon = nodes['y'].min(), nodes['x'].min(), nodes['y'].max(), nodes['x'].max()
corner_nodes = ox.distance.nearest_nodes(map_graph, (min_lat, min_lon), (max_lat, max_lon))
source_node, target_node = corner_nodes

print(f"Source node: {source_node} type: {type(source_node)}")
print(f"Target node: {target_node} type: {type(target_node)}")


def get_node_from_id(node_id):
    for node_obj in graph_nodes_with_data:
        if node_obj[0] == node_id:
            return node_obj

    return None


source_node_obj = get_node_from_id(source_node)
target_node_obj = get_node_from_id(target_node)

# print(f"Source node obj type: {type(source_node_obj)}")
# print(f"Target node obj type: {type(target_node_obj)}")



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


# A*
def get_dist(node1, node2):  # euclidean dist

    node1_data = node1[1]
    node2_data = node2[1]

    x1, y1 = node1_data['x'], node1_data['y']
    x2, y2 = node2_data['x'], node2_data['y']

    coord1 = (y1, x1)
    coord2 = (y2, x2)

    return great_circle(coord1, coord2).m


h_costs = {}  # heuristic = distance to end node
for n in graph_nodes_with_data:
    node_id = n[0]
    h_costs[node_id] = get_dist(n, target_node_obj)

g_costs = {}
for n in all_nodes:
    g_costs[n] = math.inf
g_costs[source_node] = 0

f_costs = {}  # F-cost = G-cost + H-cost
for n in all_nodes:
    f_costs[n] = math.inf
f_costs[source_node] = get_dist(source_node_obj, target_node_obj)

print("H from source: ", f_costs[source_node])

visited = {}  # visited nodes (closed set)
for n in all_nodes:
    visited[n] = False

queue = [(f_costs[source_node], source_node)]  # create a priority queue (open set)

# path reconstruction
path = []
found_solution = False
pivot_node = None  # used to reconstruct the path only


def a_star(frame):
    global found_solution, pivot_node

    # reconstruct path in each frame
    if found_solution:

        if pivot_node != source_node:
            neighbor_nodes = map_graph.neighbors(pivot_node)
            # Filter out neighbors that have no edge to them
            valid_neighbors = [neighbor for neighbor in neighbor_nodes if map_graph.has_edge(pivot_node, neighbor)]

            # Find the neighbor with the lowest cost
            min_cost = float('inf')
            min_neighbor = None
            for neighbor in valid_neighbors:
                neighbor_cost = g_costs[neighbor]
                if neighbor_cost < min_cost:
                    min_cost = neighbor_cost
                    min_neighbor = neighbor

            pivot_node = min_neighbor
            path.append(pivot_node)
        else:
            print("Done! Shortest path:", path)

        for i in range(len(path) - 1):
            # color the path
            nodeA = path[i]
            nodeB = path[i + 1]

            if (nodeA, nodeB) in all_edges:
                edge_index = all_edges.index((nodeA, nodeB))
            else:
                edge_index = all_edges.index((nodeB, nodeA))
            edge_colors[edge_index] = colors[PATH]
            plot_lc.set_colors(edge_colors)

        return

    if queue:
        current_f_cost, node = heapq.heappop(queue)  # Pop the node with the shortest distance
        if visited[node]:
            return

        visited[node] = True

        # Check if the end node is reached, reconstruct the path from end to start
        if node == target_node:
            found_solution = True
            pivot_node = node

            path.append(node)
            return

        # explore node
        neighbor_nodes = map_graph.neighbors(node)
        for neighbor in neighbor_nodes:

            if map_graph.has_edge(node, neighbor):  # some neighbors have no edge to them, god knows why

                if not visited[neighbor]:

                    edge_data = map_graph.get_edge_data(node, neighbor)
                    first_key = next(iter(edge_data))  # key is 0 or a diff number, god knows why
                    dist_to_neighbor = edge_data[first_key]['length']  # assuming there's only one edge between nodes

                    new_g_cost = g_costs[node] + dist_to_neighbor
                    if new_g_cost < g_costs[neighbor]:
                        # color as exploring
                        if (node, neighbor) in all_edges:
                            edge_index = all_edges.index((node, neighbor))
                        else:
                            edge_index = all_edges.index((neighbor, node))
                        edge_colors[edge_index] = colors[EXPLORING]
                        plot_lc.set_colors(edge_colors)

                        g_costs[neighbor] = new_g_cost  # update the G-cost for the neighbor
                        f_costs[neighbor] = new_g_cost + h_costs[neighbor]  # update the F-cost for the neighbor
                        heapq.heappush(queue, (f_costs[neighbor], neighbor))
        # color as explored


ms_per_frame = 0  # animation speed
animation = FuncAnimation(fig, a_star, interval=ms_per_frame, blit=False, cache_frame_data=False)
plt.show()
