from trajectory_lib import trace, segment as seg, tool
from matplotlib import pyplot as plt
import numpy as np

# list the parameter
fsample = 250
gradient = 0.25
n_instance = 1
level = [0.25, 0.5, 0.75, 1]

# get the trapezium
curve = trace.trapezium(slope = [gradient], level = level, randomise = False, n_instance = n_instance)
x, e = curve.bind(t_plateau= 10, fs = fsample)

# remove event from condition
dx = abs(np.diff(np.concatenate(([0], x)), n = 1))
e[dx > 0] = 0

# plot
plt.plot(x)


