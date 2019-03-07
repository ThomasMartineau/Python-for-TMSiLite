#Trajectory generator for TMSi Lite

#number crushing
import numpy as np
import itertools
import random
import scipy.integrate as integrate 

#ploting
from matplotlib import pyplot as plt

#file management
import csv

#all global constants etc
fs_default = 60

def plot_trajectory(x, freq = None, fs = fs_default):
    
    t = get_time_min(x)
    f, ax = plt.subplots()
    ax.plot(t,x)
    ax.set_xlabel('time (minutes)')
    ax.set_ylabel('%MVC')
    ax = ax.twinx()
    ax.plot(t[:-1], np.diff(x)*fs, color = 'red')
    ax.set_ylabel('%MVC/s')
    
#return time vector in minutes
def get_time_min(x, fs = fs_default):
    n = len(x)
    t = np.linspace(0, n/(fs*60), n)
    return t

#write 
def write_to_csv(name, x, y):    
    with open(name, 'w', newline = '') as target:
        w = csv.writer(target)
        for k in zip(x,y):
            w.writerow(k)

#utility function
def random_or_deterministic(x):
    #find type
    y = type(x)
    
    #deterministic
    if  y is int or y is float:
        return x
        
    #random between two points
    elif (y is list or y is tuple) and len(x) == 2:
        return np.random.rand()*(x[1] - x[0]) + x[0]

#Operation on trajectory      
def Frequency_trajectory_to_Chirp(f, fs = fs_default, A = 1):
    phi = 2*np.pi*integrate.cumtrapz(f, dx = 1/fs) - np.pi/2
    return A/2*(np.sin(phi) + 1)

##Segments---------------------------------------------------------------------    
class Segment():
    
    def __init__(self, duration = 5):
        self.duration = duration
        
    #sampling frequency next sampling frequency
    def generate(self, offset = 0, fs = fs_default):
        k = np.ones(int(self.duration*fs))
        return k*offset
    
class Ramp(Segment):
    
    def __init__(self, duration = 5):
        #superclass
        super(Ramp, self).__init__(duration)
        
    def generate(self, x0 = 0, x1 = 1, fs = fs_default):
        #time vector
        k = np.linspace(0, self.duration, int(self.duration*fs))
        return (x1-x0)/self.duration*k + x0
        
#samplign frequency is 60Hz
class Trapezium(Segment):
    
    # constructor
    def __init__(self, t_slope = 5, t_plateau = 5, level = 1, fs = fs_default):
        #complete total duration
        T = 2*t_slope + t_plateau
        super(Trapezium, self).__init__(T)
        
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
    
#second Trapezium 
class Trapezium_grad(Trapezium):
    
    #constructor grad unit/s level = 1
    def __init__(self, grad = 0.5, t_plateau = 5, level = 1, fs = fs_default):
        #duration
        t_slope = level/grad
        super(Trapezium_grad, self).__init__(t_slope, t_plateau, level, fs)
   
    
##Blocks
class Trapezium_Block():
    
    # constructor #array like of parameter #parameter 
    def __init__(self, slope = [2.5, 5, 7.5, 10], level = [0.25, 0.5, 0.75, 1], randomise = True, n_instance = 1):
        
        #generate paramter table
        table = list(itertools.product(slope, level))
        
        #label parameters
        p = [] 
        for k, c in enumerate(table):
            p += [(k + 1, c[0], c[1])]
        
        #save the table
        self.table = p
        
        #save to parameter
        p *= n_instance      
        
        if randomise:
           random.shuffle(p)
           
        self.parameter = p
              
    #time to start, time to pause (number or random interval)
    def bind(self, t_start = 5, t_pause = 5, t_plateau = 5, fs = fs_default):
        
        #initial start
        x = Segment(duration = t_start).generate(fs = fs)
        y = np.zeros_like(x); 
        
        #starting binding the segments
        for p in self.parameter:           
            #randomise does parameter if needed            
            t1 = random_or_deterministic(t_plateau)
            t2 = random_or_deterministic(t_pause)
            
            #trapezium
            trapz = Trapezium_grad(p[1], t1, p[2]).generate(fs = fs)
            pause = Segment(t2).generate(fs = fs)
            
            #append the trajectory
            x = np.append(x, trapz)
            y = np.append(y, np.ones_like(trapz)*p[0])
            x = np.append(x, pause)
            y = np.append(y, np.zeros_like(pause))            
        
        return x, y

class Ramp_Block():
    
    def __init__(self, level = [1, 2, 3], randomise = True, n_instance = 1):
        
        #generate parameter table
        tb = level
        tb *= n_instance
        if randomise:
           random.shuffle(tb)
        
        #bind
        self.parameter = tb
    
    def bind(self, t_start = 5, t_transition = 5,  t_plateau = 5, fs = fs_default):
        #segment
        x = Segment(duration = t_start).generate(fs = fs)
        
        for p in self.parameter:
            #self parameter
            plateau = Segment(t_plateau).generate(p)
            transition = Ramp(t_transition).generate(x[-1], plateau[0]);
            x = np.append(x, transition)
            x = np.append(x, plateau)
        
        return x
            
if __name__ == "__main__":
    
    #s1 = Segment(5)
    #x = s1.generate()
    #t1 = Trapezium()
    #x = t1.generate()
    #tb2 = Trapezium_grad()
    #x = tb2.generate()
    #plt.plot(x)
    

#    tb1 = Trapezium_Block(slope = [0.75, 1.25, 2.5, 5])
#    x = tb1.bind(t_pause = (2.5,5), t_plateau = (1,2.5))
#    plt.plot(x)
    
    rb = Ramp_Block(randomise = False)
    x = rb.bind()
    
    w = Frequency_trajectory_to_Chirp(x)
    

