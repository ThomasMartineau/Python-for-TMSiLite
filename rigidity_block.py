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

# 0 - high baseline
# 1 - high with random
# 2 - high on clockwise
# 3 - high on counterclockwise

# 4 - low baseline
# 5 - low rand
# 6 - low on clockwise
# 7 - low on counter clockwise

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
        if   condition[1] == 'Random':
            # define high perturbation section  
            self.perturbation = trace.rand_step(boundary = [-T, T]) 
        elif condition[1] == 'CW':
            # clock-wise perturnation 
            self.perturbation = trace.rand_step(boundary = [0, T])
        elif condition[1] == 'CCW':
            # counter-clock wise perturbation
            self.perturbation = trace.rand_step(boundary = [-T, 0])
        else:
            self.perturbation = trace.rand_step(boundary = [0, 0])
        # Meta-information
        self.time = None
                
    def assemble(self, option):
        # t_start: time at the beginning of the block
        # hold_cue: time to hold the cue
        # after_cue: time to rejoin zero hold point, without perturbation
        # occ_perturbation: time or time interval between perturbation
        
        # c: cue timeseries
        # ev: even
        # tr: trial
        # per: perturbation
        
        # start
        c, per = 2*(seg.line(option['start']).generate(fs = option['fsample']),)
        # number of perturbation
        if self.condition[0] == "High":
            n = option['high_range'] # between 4 or 6 perturbation between each cue
        elif self.condition[0] == "Low":
            n = option['low_range'] # between 10 and 12 perturbation between each cue      
        # for every level in cue
        for l in self.cue.level:    
#                #OFFSET           
#                if self.condition[4] == 'Random':
#                    offset = tool.rand_sign()*option['offset_perturbation']     
#                # clokwise
#                elif self.condition[4] == 'CW':
#                    offset = option['offset_perturbation']
#                # counter-clockwise
#                elif self.condition[4] == 'CCW':
#                    offset = -option['offset_perturbation']    
#                #None
#                elif self.condition[4] == 'None':
#                    offset = 0
            
            # PERTURBATION assembly
            p = self.perturbation.bind(n = n, t_plateau = option['hold_perturbation'], 
                                              t_pause = option['occ_perturbation'], 
                                              t_end = option['beta_window'],
                                              fs = option['fsample'])
            # append
            c = np.append(c, np.zeros_like(p))
            per = np.append(per, p)
            # for every steps 
            q = self.cue.partial_bind(l, t_prior = 0, 
                                         t_plateau = option['hold_cue'], 
                                         t_after = option['after_cue'],
                                         fs = option['fsample'])
            # append
            c = np.append(c, q)
            per = np.append(per, per[-1]*np.ones_like(q)*(abs(q) > 0))
        
        # had the end segment
        q = seg.line(option['end']).generate(fs = option['fsample'])
        c = np.append(c, q)
        per = np.append(per, q)
        
        # marking trials
        t, tr, ev = tool.get_time(c, fs = option['fsample']), np.zeros_like(c), np.zeros_like(c)
        fcue = tool.find_edges(abs(c), rise_not_fall = False)
        k1, k2 = tool.find_timeindex(t, option['start'], fs = option['fsample']), fcue[0]
        tr[k1:k2], ev[k1:k2] = 1, self.condition[-1] + 1
        for k, (k1, k2) in enumerate(zip(fcue[:-1], fcue[1:])):
            k1 = tool.find_timeindex(t, t[k1] + option['after_cue'], fs = option['fsample']) 
            tr[k1:k2], ev[k1:k2] = k + 2, self.condition[-1] + 1
                    
        # get time vector    
        self.time = tool.measure_time(c)    
        
        return {'time': t, 'cue': c, 'torque': per, 'trial': tr, 'event': ev}
    
def plot(trajectory):
    # create necessary amount of subplots    
    fig, axes = plt.subplots(len(trajectory), 1, sharex = True)
    for x, ax in zip(trajectory, axes):
        t = x['time']
        ax.plot(t, x['cue'])
        ax.plot(t, x['event']/max(x['event']))
        ax.plot(t, x['torque'])    
    ax.set(xlabel = 'time(s)') 
    return fig


def get_all_block(option, n = 4):    
    # List all blocks
    list_block = [block(n, option, ('High', None, 0)),     # 0 - high none
                  block(n, option, ('High', 'Random', 1)), # 1 - high with random
                  block(n, option, ('High', 'CW', 2)),     # 2 - high on clockwise
                  block(n, option, ('High', 'CCW', 3)),    # 3 - high on counterclockwise
                  block(n, option, ('Low', None, 4)),      # 4 - low none
                  block(n, option, ('Low', 'Random', 5)),  # 5 - low rand
                  block(n, option, ('Low', 'CW', 6)),      # 6 - low on clockwise
                  block(n, option, ('Low', 'CCW', 7))]     # 7 - low on counter clockwise
    
    return list_block  

def get_default_option():
    # empty dictionary
    option = {}
    # block design
    option['start'] = 5
    option['end'] = 5
    # cue
    option['cue'] = 4
    option['hold_cue'] = 5
    option['after_cue'] = 5
    option['max_amplitude'] = 1  
    # perturbation
    option['occ_perturbation'] = [0.5, 1]
    option['beta_window'] = 2.5
    option['hold_perturbation'] = 0.5
    option['high_range'] = [2, 4]
    option['low_range'] = [4, 8]
    option['max_torque'] = 1
    option['fsample'] = 125
    return option

if __name__ == "__main__":
    
    # left option 
    option = get_default_option()
    list_block = get_all_block(option)
    trajectory = [b.assemble(option) for b in list_block]
    plot(trajectory)
    for x in trajectory:
        x = np.vstack(x.values()).transpose()
        