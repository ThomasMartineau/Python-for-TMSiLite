# -*- coding: utf-8 -*-
# from the trajectory library
from trajectory_lib import trace, segment as seg, tool

# other
import numpy as np
from matplotlib import pyplot as plt


# TMSiLite hi5 programming
# /TMSiLite: cursor-event /Hi5: [state1-state2-...-stateN]-[para1-para2-...-paraN]
# controller 

# all fields are normalise between [-1 1] -> [left, right]

# section = [cursor, event, torque]
# description event: 
# 0 -- nothing
# 1 -- go to cue
# 2 -- baseline
# 3 -- high perturbation
# 4 -- low perturbation (left)
# 5 -- low perturbation (right) 
 
# define custom class block --> specific to experiment
class block(): #add base function   
    # main function to create the different section of the experiment 
    def __init__(self, option, condition, n_cue = 5, side = "none"):
        #super (if needed)
        
        # Block type
        self.condition = condition
        self.side = side
        
        # Cue and Perturbation
        A = option['max_amplitude']
        self.cue = trace.step(level = [-A, A], randomise = True, n_instance = n_cue) # return between left/right
        self.perturbation = None

        # Meta-information
        self.time = None
        
        # create section type 
        T = option['max_torque']
        
        if condition is "high":
            # define high perturbation section  
            self.perturbation = trace.rand_step(boundary = [-T, T])
            
        elif condition is "low" and side is not "none":
            # define low perturbation section 
            if side is "right":
                # boundary -- right 1
                self.perturbation = trace.rand_step(boundary = [0, T])
                
            elif side is "left":
                # boundary -- left -1 
                self.perturbation = trace.rand_step(boundary = [-T, 0])
                
    def assemble(self, option):
        # t_start: time at the beginning of the block
        # hold_cue: time to hold the cue
        # after_cue: time to rejoin zero hold point, without perturbation
        # occ_perturbation: time or time interval between perturbation
        
        # for the baseline
        if self.condition is "baseline":
            # bind the entire baseline
            c = self.cue.bind(t_start = option['start'], t_plateau = option['hold_cue'], t_pause = option['occ_cue'])
            
            # append
            x = np.zeros_like(c)
            m = np.zeros_like(c) + (abs(c) > 0)
            
            # tag all the series

        else:
            # start
            c, x, m = 3*(seg.line(option['start']).generate(),)
        
            if self.condition is "high":
                n = option['high_range'] # between 4 or 6 perturbation between each cue
                tag = 3
            
            elif self.condition is "low":
                n = option['low_range'] # between 10 and 12 perturbation between each cue
                
                #tag all the sides
                if self.side is "right":
                    tag = 4
                
                elif self.side is "left":
                    tag = 5
                    
            # for every level in cue
            for l in self.cue.level:
#                # offset
#                if self.condition is "high":
#                    offset = tool.rand_sign()*option['offset_perturbation']
#                
#                elif self.side is "left":
#                    offset = -option['offset_perturbation']
#                
#                elif self.side is "right":
#                    offset = option["offset_perturbation"]
#                    
                  
                # perturbation offset 
                offset = tool.rand_sign()*option['offset_perturbation']
                bound = self.perturbation.boundary
                print(self.perturbation.boundary)
                
                # perturbation assembly
                p = self.perturbation.bind(n = n, t_plateau = option['hold_perturbation'], t_pause = option['occ_perturbation'])
                #p += offset*np.ones_like(p)
                #p = np.clip(p, bound[0], bound[1])
                
                # append
                c = np.append(c, np.zeros_like(p))
                x = np.append(x, p)
                m = np.append(m, tag*np.ones_like(p))
                
                # for every steps 
                q = self.cue.partial_bind(l, t_prior = 0, t_plateau = option['hold_cue'], t_after = option['after_cue'])
                
                # append
                c = np.append(c, q)
                x = np.append(x, x[-1]*np.ones_like(q)*(abs(q) > 0))
                m = np.append(m, np.zeros_like(q) + (abs(q) > 0))
                
        # get time vector
        t = tool.get_time(c)
        self.time = tool.measure_time(c)    
        
        return np.transpose(np.vstack((t, c, x, m)))
    
    
    # utility function
    def get_boundary(self, offset):
        x = self.perturbation.boundary
        if x[0] > offset:
            x[0] = offset
                
        elif x[1] < offset:
            x[1] = offset
        return x
    
    @staticmethod    
    def plot(trajectory):
        # create necessary amount of subplots
        fig, subaxis = plt.subplots(len(trajectory), sharey = True)
        
        for traj, ax in zip(trajectory, subaxis):
            ax.plot(traj[:,0], traj[:,1:3])

        ax.set(xlabel = 'time(s)') 
        return fig
    
def get_default_option():
    # empty dictionary
    option = {}
    
    # block design
    option['start'] = 5
    
    # cue
    option['cue'] = 4
    option['hold_cue'] = 5
    option['after_cue'] = 5
    option['occ_cue'] = [3, 5]
    option['max_amplitude'] = 1
     
    # perturbation
    option['occ_perturbation'] = [0.5, 1]
    option['hold_perturbation'] = 0.5
    option['high_range'] = [3,5]
    option['low_range'] = [4,6]
    option['max_torque'] = 1
    option['offset_perturbation'] = 0.25
    
    return option

if __name__ == "__main__":
    
    option = get_default_option()
    
#    plt.figure()
#    b = block(option, "high", n_cue = 1)
#    x = b.assemble(option)
#    plt.plot(x[:,0], x[:,1], x[:,0], x[:,2])
#    #plt.plot(x[:,0],x[:,-1])
#    
    plt.figure()
    b = block(option, "low", n_cue = 1, side = 'left')
    x = b.assemble(option)
    plt.plot(x[:,0], x[:,1], x[:,0], x[:,2])