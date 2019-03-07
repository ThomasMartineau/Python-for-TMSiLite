import trajectory_lib as lib
from matplotlib import pyplot as plt
import numpy as np

#ramps
#block design
slope = [0.1, 0.25, 0.5] #MVC per second
level = [0.5, 1] 
block1 = lib.Trapezium_Block(slope, level, n_instance = 5, randomise = True)
               
#create trajectory
x1, y = block1.bind(t_pause = (2.5, 5), t_plateau = 2.5) #2.5~5 pause between ramps &  1~2.5 plateau
lib.plot_trajectory(x1)

#save localy for now
lib.write_to_csv('ramp.csv', x1, y)
print("Ramp experiments last for: ", lib.get_time_min(x1)[-1], "minutes")

#chirp
#block design
freq = [1] #frequency to reach
n = 5
block2 = lib.Ramp_Block(freq)
f = block2.bind(t_start = 5, t_plateau = 1, t_transition = 60)

#chip transformation
w = lib.Frequency_trajectory_to_Chirp(f, A = 0.8)
w = np.tile(w, 5)
lib.plot_trajectory(w)

#save localy for now
lib.write_to_csv('chirp.csv', w, f)
print("Chirp experiments last for: ", lib.get_time_min(w)[-1], " minutes")





