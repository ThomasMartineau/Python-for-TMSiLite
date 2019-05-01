# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 13:37:05 2019

@author: tlm111
"""
from scipy import signal
from matplotlib import pyplot as plt

fc = 1
fs = 50

b, a = signal.butter(4, 2*fc/fs, btype = 'high')


# Plot
w, h = signal.freqz(b, a)
plt.plot(w, abs(h))