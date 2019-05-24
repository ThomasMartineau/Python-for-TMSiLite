# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 13:37:05 2019

@author: tlm111
"""
from scipy import signal
from matplotlib import pyplot as plt

fs = 50

# high filter
fc = 1
b, a = signal.butter(4, 2*fc/fs, btype = 'high')
print("high pass:", b, a)

# Plot
w, h = signal.freqz(b, a)
plt.plot(w, abs(h))


# notch filter
fc = 5
b, a = signal.butter(4, 2*fc/fs, btype = 'low')
print("low pass:", b, a)

# Plot
w, h = signal.freqz(b, a)
plt.plot(w, abs(h))