from trajectory_lib import trace, segment as seg, tool
from matplotlib import pyplot as plt
import numpy as np
from scipy import signal
from scipy.stats import linregress

# list the parameter
fsample = 250
gradient = 0.10
n_instance = 2
level = [0.25, 0.5, 0.75, 1]
N = len(level)

# get the trapezium
curve = trace.trapezium(slope = [gradient], level = level, randomise = False, n_instance = 1)
x, e = curve.bind(t_plateau= 10, fs = fsample)
# remove event from condition
dx = abs(np.diff(np.concatenate(([0], x)), n = 1))
e[dx > 0] = 0
# filter
for k in range(1, e.shape[0] - 1):
    # the shape
    if e[k-1] == 0 and e[k] > 0 and e[k+1] == 0:
        e[k] = 0
# apply symetry
x = np.concatenate((x,-x))
e = np.concatenate((e, e))

# analysis code -- generate analysis code
emg = np.transpose(np.random.randn(4, x.shape[0])*x)
torque = x + 0.1*np.random.randn(x.shape[0])
# preprocessing # use butterwidth filter
norder = 4
fn = fsample/2
fb = 2, 100
wn = fb[0]/fn, fb[1]/fn
[b,a] = signal.butter(norder, wn, btype = 'bandpass')
emg = signal.filtfilt(b, a, emg, axis = 0) 
extr_emg = np.max(emg), np.min(emg)
# split (top half)
emg = np.split(emg, 2)
x = np.split(x, 2)
e = np.split(e, 2)
torque = np.split(torque, 2)
label = ['Extensor\n digitorum', 'Extensor\n carpi radialis', 'Flexor\n carpi ulnaris', 'Flexor\n palamaris longus']

# scope
fig = {}
fig['emg'], axes = plt.subplots(5, 2)
# plot the trace
for k, (emg_side, x_side) in enumerate(zip(emg, x)):
    # keep the time constraints
    N = emg_side.shape[0]
    T = N/fsample
    t = np.linspace(0, T, N) 
    # plot the trajectory
    ax = axes[0, k]
    ax.plot(t, x_side, 'r')
    # do the flexion
    for l, (m, lb) in enumerate(zip(np.rollaxis(emg_side, axis = 1), label)):
        # get the correct axis
        ax = axes[l + 1, k]
        ax.plot(t, m)
        ax.set_ylabel(lb)
        ax.set_ylim(*extr_emg)

# analyse
RMS = lambda x: np.sqrt(np.mean(x**2, axis = 0))
# analyse the segment    
analysis = {}
analysis['rms'] = []
analysis['spectra'] = []
analysis['torque'] = []
# signal processing pipeline
for k, (emg_side, e_side, tor_side) in enumerate(zip(emg, e, torque)):
    # for every segment
    for l in range(0, int(np.max(e_side))):
        # segment
        emg_seg = emg_side[e_side == l]
        # apply root mean square
        analysis['rms'].append(RMS(emg_seg))
        analysis['spectra'].append(signal.welch(emg_seg, fs = fsample, axis = 0))
        # torque segment
        tor_seg = tor_side[e_side == 1]
        analysis['torque'].append(np.mean(tor_seg))
        
# splity every element into two
for key, value in analysis.items():
    # split something
    n = len(value)//2
    ext, flex = value[:n], value[n:]
    # except for the spectra
    if key == 'rms':
        analysis[key] = np.vstack(ext), np.vstack(flex)
    elif key == 'spectra':
        analysis[key] = ext, flex
    elif key == 'torque':
        analysis[key] = np.stack(ext), np.stack(flex)
        
# plot the result
fig['rms'], axes = plt.subplots(4, 2, sharey = True)
for k, rms_side in enumerate(analysis['rms']):
    for l, (r, lb) in enumerate(zip(np.rollaxis(rms_side, axis = -1), label)):
        ax = axes[l, k]
        w = np.arange(0, len(rms_side))
        ax.bar(w, r)
        ax.set_ylabel(lb)

# plot the results
fig['spectra'], axes = plt.subplots(len(analysis['spectra'][0]), 2, sharey = True)
dB = lambda x: 20*np.log10(abs(x))
min_Pxx, max_Pxx = 0, 0
for k, spectra_side in enumerate(analysis['spectra']):
    # for every spectra
    for l, (w, X) in enumerate(spectra_side):
        # all the axes
        ax = axes[l, k]
        Pxx = dB(X)
        # select the min, max
        select = np.logical_and(wn[0] < w/fn, w/fn < wn[1])
        # plot
        ax.plot(w[select], Pxx[select])
        ax.set_xlim(*fb)
        if l == 0:
            ax.legend(label, loc = 'right')
            
# regression ?
            
# export results
            
            


    
    
    
    

        
    





