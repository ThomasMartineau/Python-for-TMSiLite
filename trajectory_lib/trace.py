#ploting
from matplotlib import pyplot as plt

#number crushing tools
import numpy as np
import itertools
import random

# all global constants etc
fs_default = 50

if __name__ is not "__main__":
    from trajectory_lib  import tool 
    from trajectory_lib  import segment as seg
else:   
    import tool 
    import segment as seg

    
class step():
    # constructor
    def __init__(self, level = [0.25, 0.5, 0.75, 1], randomise = False,  n_instance = 1):
        # copy the number of instance
        level *= n_instance      
        
        # shuffle the levels
        if randomise:
            random.shuffle(level)      
        
        # levels 
        self.level = level
        
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
                        

class rand_step():
    # constructor
    def __init__(self, boundary = [0, 1]):
        # constructor
        self.boundary = boundary
              
    def bind(self, n = 10, offset = 0, t_start = 0, t_plateau = 5, t_pause = 5, t_end = 0, fs = fs_default):        
        # overwrite constructor -> no offset
        self.offset = offset
        
        # initial start
        x = seg.line(duration = t_start + tool.rand_or_det(t_pause)).generate(offset = offset, fs = fs)
        
        # pause -- plateau -- pause
        for l in self.get_level(n, offset):
 
           # append
           t1 = tool.rand_or_det(t_plateau)
           step = seg.line(t1).generate(offset = l, fs = fs)
           x = np.append(x, step)
            
           t2 = tool.rand_or_det(t_pause)
           pause = seg.line(t2).generate(offset = offset, fs = fs)
           x = np.append(x, pause)  
           
           x = np.append(x, seg.line(duration = t_end).generate(offset = offset, fs = fs))
           
        return x
        
    # define level level property
    def get_level(self, n = 1, offset = 0):
        # change the number of instance
        n = tool.rand_or_det(n, discrete = True)
        bound = self.get_boundary(offset)
        # random
        return tool.rand_interval(bound, n = n)
    
    # define the boundary property
    def get_boundary(self, offset = 0):
        x = self.boundary.copy()
        # offset
        x[0] += offset
        x[1] += offset
        
        # clip
        if x[0] < -1:
            x[0] = -1
        elif x[1] > 1:
            x[1] = 1       
        return x
            
    
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

class ramp():
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
        x = seg.line(duration = t_start).generate(offset = self.parameter[0], fs = fs)
        
        for p in self.parameter[1:]:
            plateau = seg.line(t_plateau).generate(p)
            transition = seg.ramp(t_transition).generate(x[-1], plateau[0]);
            x = np.append(x, transition)
            x = np.append(x, plateau)
        
        return x
    
if __name__ == "__main__":

#    plt.plot(step().bind(offset = 0.25))
#    
#    s = rand_step(boundary = [0, 1])
#    x = s.bind(n = 5, offset = -0.25)
#    plt.plot(x)
#        
#    x,_ = trapezium().bind()
#    plt.plot(x)
    
     chirp = ramp(level = [0.5,1], randomise = False, n_instance = 1)   
     f = chirp.bind(t_start = 5, t_transition = 60, t_plateau = 5)
     w = tool.frequency_trajectory_to_chirp(f) 
     tool.plot_trajectory(f)
     tool.plot_trajectory(w)