#ploting
from matplotlib import pyplot as plt

#number crushing tools
import numpy as np
import itertools
import random

#other sub-modules
from trajectory_lib import tool
from trajectory_lib import segment as seg

# all global constants etc
fs_default = 60

    
class step():
    # constructor
    def __init__(self, level = [0.25, 0.5, 0.75, 1], randomise = False,  n_instance = 1):
        # copy the number of instance
        level *= tool.rand_or_det(n_instance, discrete = True)
         
        # shuffle the levels
        if randomise:
            random.shuffle(level)
        
        # levels 
        self.level = level
        self.n = n_instance
        
        
    # assemble the block -- one step at the time in a inner method loop
    def bind(self, offset = 0,  t_start = 0, t_plateau = 5, t_pause = 5, t_end = 0, fs = fs_default):
        # initial start
        x = seg.line(duration = t_start + tool.rand_or_det(t_pause)).generate(offset = offset, fs = fs)
        
        # pause -- plateau -- pause
        for l in self.level:
           # append
           t1 = tool.rand_or_det(t_plateau)
           step = seg.line(t1).generate(offset = l, fs = fs)
           x = np.append(x, step)
            
           t2 = tool.rand_or_det(t_pause)
           pause = seg.line(t2).generate(offset = offset, fs = fs)
           x = np.append(x, pause)       
        
        return np.append(x, seg.line(duration = t_end).generate(offset = offset, fs = fs))
    
    # assemble the trace one-level at the time in an external loop, is open-ended
    def partial_bind(self, l, t_prior = 5 , t_plateau = 5, t_after = 5, fs = fs_default):
        
        t1 = tool.rand_or_det(t_prior)
        x = seg.line(t1).generate(offset = 0, fs = fs)
        
        t2 = tool.rand_or_det(t_plateau)
        step = seg.line(t2).generate(offset = l, fs = fs)
        x = np.append(x, step)
        
        t3 = tool.rand_or_det(t_after)
        after = seg.line(t3).generate(offset = 0, fs = fs)
        x = np.append(x, after)    
        
        return x
                        

class rand_step(step):
    # constructor
    def __init__(self, boundary = [0, 1]):
        # limits of the random distrubution 
        self.boundary = boundary
        
        # constructor
        super(rand_step, self).__init__(level = 1,  n_instance = 1) # per default -- they will be re-drawn every time bind is called
    
    def bind(self, n = 10, offset = 0, t_start = 0, t_plateau = 5, t_pause = 5, t_end = 0, fs = fs_default):
        # re-draw distribution
        self.redraw(n)
        # overwrite constructor
        return super(rand_step, self).bind(offset, t_start, t_plateau , t_pause , t_end , fs = fs_default)
    
    # re-define bind
    def redraw(self, n):
        # change the number of instace
        n = tool.rand_or_det(n, discrete = True)
        # random
        self.level = tool.rand_interval(self.boundary, n = n)
        self.n = n
        
class randn_step(step):
    # constructor
    def __init__(self, mu = 0, sig = 0, n_instance = 10):
        pass
       
class trapezium(): 
    # constructor #array like of parameter #parameter 
    def __init__(self, slope = [0.25, 0.5, 0.75, 1], level = [0.25, 0.5, 0.75, 1], randomise = True, n_instance = 1): 
        #generate paramter table
        table = list(itertools.product(slope, level))        
        
        #label parameters
        p = [(k + 1, c[0], c[1]) for k, c in enumerate(table)]
        
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
        x = seg.line(duration = t_start).generate(fs = fs)
        y = np.zeros_like(x); 
        
        #starting binding the segments
        for p in self.parameter:           
            #randomise does parameter if needed            
            t1 = tool.rand_or_det(t_plateau)
            t2 = tool.rand_or_det(t_pause)         
            #trapezium
            trapz = seg.trapezium_grad(p[1], t1, p[2]).generate(fs = fs)
            pause = seg.line(t2).generate(fs = fs) 
            #append the trajectory
            x = np.append(x, trapz)
            y = np.append(y, np.ones_like(trapz)*p[0])
            x = np.append(x, pause)
            y = np.append(y, np.zeros_like(pause))            
        
        return x, y

class ramp_block():
    # constructor
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
        x = seg.line(duration = t_start).generate(fs = fs)
        
        for p in self.parameter:
            plateau = seg.line(t_plateau).generate(p)
            transition = seg.ramp(t_transition).generate(x[-1], plateau[0]);
            x = np.append(x, transition)
            x = np.append(x, plateau)
        
        return x
    
if __name__ == "__main__":

    #plt.plot(step().bind(offset = 0.25))
    
    plt.plot(rand_step(boundary = [-1, 1]).bind(n = [5, 10], offset = 0.25, t_plateau= 0.5))
    
    #x,_ = trapezium().bind()
    #plt.plot(x)
    
    #plt.plot(ramp_block().bind())