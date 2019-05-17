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
# 1 - high with random
# 2 - high on clockwise
# 3 - high on counterclockwise
# 4 - low rand
# 5 - low on clockwise
# 6 - low on counter clockwise

# define custom class block --> specific to experiment
class block(): #add base function   
    # main function to create the different section of the experiment 
    def __init__(self, n, option, condition):        
        # Block Type
        self.condition = condition
        
        # Cue
        A = option['max_amplitude']
        self.cue = trace.step(level = [-A, A], randomise = True, n_instance = n) # return between left/right
        self.perturbation = None

        # Perturbation 
        T = option['max_torque']
    
        # direction of the perturbation
        if condition[3] == 'Random':
            # define high perturbation section  
            self.perturbation = trace.rand_step(boundary = [-T, T])
        
        elif condition[3] == 'CW':
            # clock-wise perturnation 
            self.perturbation = trace.rand_step(boundary = [0, T])
        
        elif condition[3] == 'CCW':
            # counter-clock wise perturbation
            self.perturbation = trace.rand_step(boundary = [-T, 0])
            
        # Meta-information
        self.time = None
                
    def assemble(self, option):
        # t_start: time at the beginning of the block
        # hold_cue: time to hold the cue
        # after_cue: time to rejoin zero hold point, without perturbation
        # occ_perturbation: time or time interval between perturbation
        
        # for the baseline
        if self.condition[2] == 'Baseline':
            # bind the entire baseline
            c = self.cue.bind(t_start = option['start'], t_plateau = option['hold_cue'], t_pause = option['occ_cue'])
                        
            # append
            x = np.zeros_like(c)
            m = np.zeros_like(c)
            
        else:
            # start
            c, x, m = 3*(seg.line(option['start']).generate(),)
            
            # event tag 
            tag = self.condition[0]
            
            # number of perturbation
            if self.condition[2] == "High":
                n = option['high_range'] # between 4 or 6 perturbation between each cue
            
            elif self.condition[2] == "Low":
                n = option['low_range'] # between 10 and 12 perturbation between each cue
                 
            # for every level in cue
            for l in self.cue.level:    
                #OFFSET
                # random
                #offset = tool.rand_sign()*option['offset_perturbation']
                
                if self.condition[4] == 'Random':
                    offset = tool.rand_sign()*option['offset_perturbation']     
                # clokwise
                elif self.condition[4] == 'CW':
                    offset = option['offset_perturbation']
                # counter-clockwise
                elif self.condition[4] == 'CCW':
                    offset = -option['offset_perturbation']    
                #None
                elif self.condition[4] == 'None':
                    offset = 0
                
                # PERTURBATION assembly
                p = self.perturbation.bind(n = n, offset = offset, t_plateau = option['hold_perturbation'], t_pause = option['occ_perturbation'], t_end = option['beta_window'])
                
                # append
                c = np.append(c, np.zeros_like(p))
                x = np.append(x, p)
                m = np.append(m, tag*np.ones_like(p))
                
                # for every steps 
                q = self.cue.partial_bind(l, t_prior = 0, t_plateau = option['hold_cue'], t_after = option['after_cue'])
                
                # append
                c = np.append(c, q)
                x = np.append(x, x[-1]*np.ones_like(q)*(abs(q) > 0))
                m = np.append(m, np.zeros_like(q))
                
        # get time vector
        t = tool.get_time(c)
        self.time = tool.measure_time(c)    
        
        return np.transpose(np.vstack((t, c, x, m)))
    
def plot(trajectory):
    # create necessary amount of subplots
    fig, subaxis = plt.subplots(len(trajectory), sharey = True)
    
    for x, ax in zip(trajectory, subaxis):
        ax.plot(x[:,0], x[:,1:3])
        ax.set_ylabel('Block ' + str(max(x[:,3])))

    ax.set(xlabel = 'time(s)') 
    return fig


def get_all_block(option, n = 2):    
    # List all blocks
    list_block = [block(n, option, ('Baseline', None)), # 0 - baseline
                  block(n, option, ('High', 'Random')),   # 1 - high with random
                  block(n, option, ('High', 'CW')),     # 2 - high on clockwise
                  block(n, option, ('High', 'CCW')),    # 3 - high on counterclockwise
                  block(n, option, ('Low', 'Random')), # 4 - low rand
                  block(n, option, ('Low', 'CW')),   # 5 - low on clockwise
                  block(n, option, ('Low', 'CCW'))]  # 6 - low on counter clockwise
    
    return list_block  

def get_default_option():
    # empty dictionary
    option = {}
    
    # block design
    option['start'] = 5
    option['handle'] = 'right'
    
    # cue
    option['cue'] = 4
    option['hold_cue'] = 5
    option['after_cue'] = 5
    option['occ_cue'] = [3, 5]
    option['max_amplitude'] = 1
     
    # perturbation
    option['occ_perturbation'] = [0.5, 1]
    option['beta_window'] = 2.5
    option['hold_perturbation'] = 0.5
    option['high_range'] = [3,5]
    option['low_range'] = [4,6]
    option['max_torque'] = 1
    option['offset_perturbation'] = 0.25
    
    return option

if __name__ == "__main__":
    
    # left option 
    option = get_default_option()
    list_block = get_all_block(option)
    x = []
    
    for k, b in enumerate(list_block):
        print(k)
        x += [b.assemble(option)]
    
    plot(x)
    