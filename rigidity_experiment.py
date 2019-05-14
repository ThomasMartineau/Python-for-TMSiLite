# Qt GUI tools
import sys
import os 
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.uic import loadUi

from trajectory_lib import tool
import rigidity_block as experiment
from matplotlib import pyplot as plt
import numpy as np
import random

# Main windows 
class main_window(QMainWindow):
    # initiate the window
    def __init__(self):
        # superclass and load gui from designer 
        super(main_window, self).__init__()
        
        loadUi(os.getcwd() + '\\gui\\rigidity_experiment_main_window.ui', self)
        
        # internal state
        self.trajectory = None
        self.table = None
        self.option = None
        
        # define button behaviour
        self.preview_button.clicked.connect(self.preview)
        self.generate_button.clicked.connect(self.generate)
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
                
                # add a table file
                
                
                
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
            self.shuffle_block.setChecked(option['randomise'])
            
            if option['handle'] is 'left':
                self.handle.setChecked(option['handle'])
            
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
            self.beta_window.setValue(option['beta_window'])
            self.per_holding_time.setValue(option['hold_perturbation'])
            self.high_perturbation_min_number.setValue(option['high_range'][0])
            self.high_perturbation_max_number.setValue(option['high_range'][1])
            self.low_perturbation_min_number.setValue(option['low_range'][0])
            self.low_perturbation_max_number.setValue(option['low_range'][1])
            self.torque.setValue(option['max_torque'])
            self.offset.setValue(option['offset_perturbation'])
            
            print("[SUCCESS] all option loaded")
            
    
    def get_condition(self):
        # block
        condition = []
                     
        # do list comprehension literraly
        for k in range(0, 7):
            k = str(k)
            # if the block is checked
            if eval("self.block_" + k + ".isChecked()"):                    
                condition += [(eval("self.type_" + k + ".currentText()"), eval("self.offset_" + k  + ".currentText()"))]

        return condition
        
    
    def get_option(self):
        print('retriving block and trajectory options')
        # empty dictionary
        option = {}
        
        # Block design
        option['start'] = self.start_time.value()
        option['repetition'] = self.repetition.value()
        option['randomise'] = self.shuffle_block.isChecked()
        
        # Hi5 handle setup
        if self.handle.isChecked():
            option['handle'] = 'left'
        else:
            option['handle'] = 'right'
        
        # Cue
        option['cue'] = self.number_cue.value()//2
        option['hold_cue'] = self.cue_holding_time.value()
        option['after_cue'] = self.cue_return_time.value()
        t = [self.cue_min_time.value(), self.cue_max_time.value()]
        option['occ_cue'] = sorted(t)
        option['max_amplitude'] = self.max_amplitude.value()
         
        # Perturbation
        t = [self.per_min_time.value(), self.per_max_time.value()]
        option['occ_perturbation'] = sorted(t)
        option['beta_window'] = self.beta_window.value()
        option['hold_perturbation'] = self.per_holding_time.value()
        x = [self.high_perturbation_min_number.value(), self.high_perturbation_max_number.value()]
        option['high_range'] = sorted(x)
        x = [self.low_perturbation_min_number.value(), self.low_perturbation_max_number.value()]
        option['low_range'] = sorted(x)
        option['max_torque'] = self.torque.value()
        option['offset_perturbation'] = self.offset.value()
        
        # Consol output
        print(option)
        return option
              
    @pyqtSlot()
    def preview(self):
        print('generating preview trajectory')
        option = self.get_option()
        condition = self.get_condition()
        list_block = [experiment.block(2, option, c) for c in condition]
        trajectory = [b.assemble(option) for b in list_block]
        print('[SUCCESS] all preview trajectory generated')

        experiment.plot(trajectory)
        plt.show()
        
    @pyqtSlot()
    def generate(self):
        # create an option dictionary and the condition list
        print('retrieving block and trajectory options')
        option = self.get_option()
        condition = self.get_condition()
        
        # find the number of cue
        n = option['cue']
        
        #creat a block list
        list_block = [experiment.block(n, option, c) for c in condition]
                
        # manipulate the lsit
        b0 = list_block[0]
        list_block = list_block[1:]
        
        # manipulate
        list_block *= option['repetition']
        
        # random the option
        if option['randomise']:
            random.shuffle(list_block)
            
        # replace the line on top
        list_block = [b0] + list_block   
                           
        # assemble all blocks -> all random instances of the block wahts        
        print('generating trajectories for each block')
        self.trajectory = [b.assemble(option) for b in list_block]
        print('[SUCCESS] all trajectory generated')
        
        time = [traj[-1, 0] for traj in self.trajectory]
        
        # time
        self.Total_time.display(tool.convert_sec(sum(time), string = True))
        self.Average_time.display(tool.convert_sec(np.mean(time), string = True))
        
        print('saving options and condition')
        self.option = option
        self.table = None
        
        
if __name__ == "__main__":
  
    # start the app
    app = QApplication(sys.argv)
    widget = main_window()
    widget.show()
    sys.exit(app.exec_())
    
    
