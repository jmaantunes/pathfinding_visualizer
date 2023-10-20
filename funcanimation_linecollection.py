import random
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.animation as animation

lines = []
for i in range(10):
    lines.append([(0, i), (10, i)])

fig, ax = plt.subplots()
colors = np.random.random(len(lines)) * 255


rgb_colors = [(1, 0, 0)] * 10
lc = LineCollection(lines, colors=rgb_colors, linewidth=1)
ax.add_collection(lc)
ax.autoscale()


def update(frames):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    colors = [(r, g, b) for _ in range(len(lines))]

    ax.collections[0].set_colors(colors)


ani = animation.FuncAnimation(fig, update, frames=100, interval=200, repeat=True)
plt.show()
