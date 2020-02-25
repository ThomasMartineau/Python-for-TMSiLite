#ploting
from matplotlib import pyplot as plt

#number crushing tools
import numpy as np

# all global constants etc
fs_default = 50

##Segments---------------------------------------------------------------------    
class line():
    #constructor
    def __init__(self, duration = 5):
        self.duration = duration
        
    #sampling frequency next sampling frequency
    def generate(self, offset = 0, fs = fs_default):
        k = np.ones(int(self.duration*fs))
        return k*offset
  
class ramp(line):
    # constructor
    def __init__(self, duration = 5):
        #superclass
        super(ramp, self).__init__(duration)
        
    def generate(self, x0 = 0, x1 = 1, fs = fs_default):
        #time vector
        k = np.linspace(0, self.duration, int(self.duration*fs))
        return (x1 - x0)/self.duration*k + x0
        
class trapezium(line):
    # constructor
    def __init__(self, t_slope = 5, t_plateau = 5, level = 1, fs = fs_default):
        #complete total duration
        T = 2*t_slope + t_plateau
        super(trapezium, self).__init__(T)
        #parameter
        self.segment = (t_slope, t_plateau + t_slope)
        self.level = level
        self.gradient = level/t_slope
    
    # generate the slope
    def generate(self, offset = 0, fs = fs_default):
        #time vector
        k = np.linspace(0, self.duration, int(self.duration*fs))
        #trapezium segment
        rise = (self.gradient*k)*(k < self.segment[0]) 
        steady = self.level*((self.segment[0] <= k) ^ (k >= self.segment[1]))
        fall = (self.level - self.gradient*(k-self.segment[1]))*(self.segment[1] < k) 
        #superimposition + vertical shift
        return  (rise + steady + fall) + offset
    
class trapezium_grad(trapezium):
    #constructor grad unit/s level = 1
    def __init__(self, grad = 0.5, t_plateau = 5, level = 1, fs = fs_default):
        #duration
        t_slope = level/grad
        super(trapezium_grad, self).__init__(t_slope, t_plateau, level, fs)
               
if __name__ == "__main__":

    plt.plot(line().generate())
    plt.plot(ramp().generate())
    plt.plot(trapezium().generate())
    plt.plot(trapezium_grad().generate())