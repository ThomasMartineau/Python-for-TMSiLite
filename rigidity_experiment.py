# Qt GUI tools
import sys
import os 
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.uic import loadUi

# from the trajectory library
from trajectory_lib import trace, segment as seg, tool

# other
import numpy as np
from matplotlib import pyplot as plt
import random

# Main windows 
class main_window(QMainWindow):
    # initiate the window
    def __init__(self):
        # superclass and load gui from designer 
        super(main_window, self).__init__()
        loadUi('gui\\rigidity_experiment_main_window.ui', self)
        
        # internal state
        self.option = None
        self.trajectory = None
        
        # define button behaviour
        self.generate_button.clicked.connect(self.generate)
        self.preview_button.clicked.connect(self.preview)
        self.save_button.clicked.connect(self.save)
        self.load_button.clicked.connect(self.load)
     
    @pyqtSlot()
    def save(self):
        # get the target directory
        try:
            target = QFileDialog.getExistingDirectory(self, "Select an Empty Directory")
        except:
            target = ''
        
        if target is not '':
            # check that the directory is empty
            if len(os.listdir(target)) is 0:
                # if the trajectory haven't been generated, generate them
                if self.trajectory is None: self.generate() 
                    
                # add the config file
                name = target + "//Config" + ".csv"
                tool.write_to_csv(name, self.option)
                
                # write the trajectories
                for k, X in enumerate(self.trajectory):
                    name = target + "//Block_" + str(k) + ".csv"
                    print(name)
                    tool.write_to_csv(name, X, header = ["time", "cue", "torque", "event"])
                
                print("[SUCCESS] all file saved")
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText('Enable to save: target directory needs to be empty')
                msg.setWindowTitle("Error")
                msg.exec_()
    
    @pyqtSlot()
    def load(self):
        # load a config file
        try:
            target, _ = QFileDialog.getOpenFileName(self)
            print(target)
            
        except:
            target = ''
            
        if target is not '':
            # get the option
            option = tool.clean_csv_dict(tool.read_to_csv(target))
            
            # block design
            self.start_time.setValue(option['start'])
            self.baseline.setValue(option['baseline'])
            self.high_perturbation.setValue(option['high'])
            self.perturbation_right.setValue(option['low_right'])
            self.perturbation_left.setValue(option['low_left'])
            self.shuffle_block.setChecked(option['randomise'])
            
            # cue
            self.number_cue.setValue(2*option['cue'])
            self.cue_holding_time.setValue(option['hold_cue'])
            self.cue_return_time.setValue(option['after_cue'])
            self.cue_min_time.setValue(option['occ_cue'][0])
            self.cue_max_time.setValue(option['occ_cue'][1])
            self.max_amplitude.setValue(option['max_amplitude'])
            
            # perturbation
            self.per_min_time.setValue(option['occ_perturbation'][0])
            self.per_max_time.setValue(option['occ_perturbation'][1])
            self.per_holding_time.setValue(option['hold_perturbation'])
            self.high_perturbation_min_number.setValue(option['high_range'][0])
            self.high_perturbation_max_number.setValue(option['high_range'][1])
            self.low_perturbation_min_number.setValue(option['low_range'][0])
            self.low_perturbation_max_number.setValue(option['low_range'][1])
            self.torque.setValue(option['max_torque'])
            
            print("[SUCCESS] all option loaded")

    def get_option(self):
        # empty dictionary
        option = {}
        
        # block design
        option['start'] = self.start_time.value()
        option['baseline'] = self.baseline.value()
        option['high'] = self.high_perturbation.value()
        option['low_right'] = self.perturbation_right.value()
        option['low_left'] = self.perturbation_left.value()
        option['randomise'] = self.shuffle_block.isChecked()
        
        # cue
        option['cue'] = self.number_cue.value()//2
        option['hold_cue'] = self.cue_holding_time.value()
        option['after_cue'] = self.cue_return_time.value()
        t = [self.cue_min_time.value(), self.cue_max_time.value()]
        option['occ_cue'] = sorted(t)
        option['max_amplitude'] = self.max_amplitude.value()
         
        # perturbation
        t = [self.per_min_time.value(), self.per_max_time.value()]
        option['occ_perturbation'] = sorted(t)
        option['hold_perturbation'] = self.per_holding_time.value()
        x = [self.high_perturbation_min_number.value(), self.high_perturbation_max_number.value()]
        option['high_range'] = sorted(x)
        x = [self.low_perturbation_min_number.value(), self.low_perturbation_max_number.value()]
        option['low_range'] = sorted(x)
        option['max_torque'] = self.torque.value()
        print(option)
        
        return option
    
    @pyqtSlot()
    def preview(self):
        
        print('retriving block and trajectory options')
        #created an option dictionary option
        option = self.get_option()
        
        print('generating preview trajectory')
        #one instance of each block, with 3 cue
        n = 2
        list_block = [block(option, 'baseline', n_cue = n), block(option, 'high', n_cue = n),  block(option, 'low', n_cue = n, side = 'right'), block(option, 'low', n_cue = n, side = 'left')]        
        trajectory = [b.assemble(option) for b in list_block]
        
        print('[SUCCESS] all preview trajectory generated')
        
        fig = block.plot(trajectory)
        fig.show()
    
    @pyqtSlot()
    def generate(self):
        
        # create an option dictionary option 
        print('retrieving block and trajectory options')
        option = self.get_option()
        
        # Block Design 
        list_block = []
        
        # Baseline
        list_block += [block(option, 'baseline', n_cue = option['cue'])] * option['baseline']
        
        # High Perturbation
        list_block += [block(option, 'high', n_cue = option['cue'])] * option['high']
        
        # Low Perturbation 
        list_block += [block(option, 'low', n_cue = option['cue'], side = 'left')] * option['low_left']
        list_block += [block(option, 'low', n_cue = option['cue'], side = 'right')] * option['low_right']
       
        # schulffle all trials except the first baseline if radio button is engaged 
        if option['randomise']:
            b0 = list_block[0]
            list_block = list_block[1:]
            random.shuffle(list_block)
            list_block = [b0] + list_block
        
        
        # assemble all blocks -> all random instances of the block wahts        
        print('generating trajectories for each block')
        self.trajectory = [b.assemble(option) for b in list_block]
        self.option = option
        
        print('[SUCCESS] all trajectory generated')
        
        time = [traj[-1, 0] for traj in self.trajectory]
        
        # time
        print(time)
        self.Total_time.display(tool.convert_sec(sum(time), string = True))
        self.Average_time.display(tool.convert_sec(np.mean(time), string = True))
        #print(np.mean(time))
        
        
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
                # perturbation 
                p = self.perturbation.bind(n = n, t_plateau = option['hold_perturbation'], t_pause = option['occ_perturbation'])
                
                # append
                c = np.append(c, np.zeros_like(p))
                x = np.append(x, p)
                m = np.append(m, tag*np.ones_like(p))
                
                # for every steps 
                q = self.cue.partial_bind(l, t_prior = 0, t_plateau = option['hold_cue'], t_after = option['after_cue'])
                
                # append
                c = np.append(c, q)
                x = np.append(x, np.zeros_like(q))
                m = np.append(m, np.zeros_like(q) + (abs(q) > 0))
                
        # get time vector
        t = tool.get_time(c)
        self.time = tool.measure_time(c)    
        
        return np.transpose(np.vstack((t, c, x, m)))
    
    # utility function
    @staticmethod    
    def plot(trajectory):
        # create necessary amount of subplots
        fig, subaxis = plt.subplots(len(trajectory), sharey = True)
        
        for traj, ax in zip(trajectory, subaxis):
            ax.plot(traj[:,0], traj[:,1:3])

        ax.set(xlabel = 'time(s)')     
        return fig

if __name__ == "__main__":
    
    # start the app
    app = QApplication(sys.argv)
    widget = main_window()
    widget.show()
    sys.exit(app.exec_())
    
    
