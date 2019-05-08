# Qt GUI tools
import sys
import os 
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.uic import loadUi

from trajectory_lib import tool
import rigidity_block as experiment
from matplotlib import pyplot as plt
import random

# Main windows 
class main_window(QMainWindow):
    # initiate the window
    def __init__(self):
        # superclass and load gui from designer 
        super(main_window, self).__init__()
        
        loadUi(os.getcwd() + '\\gui\\rigidity_experiment_main_window.ui', self)
        
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
            self.offset.setValue(option['offset_perturbation'])
            
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
        option['offset_perturbation'] = self.offset.value()
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
        list_block = [experiment.block(option, 'baseline', n_cue = n), experiment.block(option, 'high', n_cue = n),  experiment.block(option, 'low', n_cue = n, side = 'right'), experiment.block(option, 'low', n_cue = n, side = 'left')]        
        trajectory = [b.assemble(option) for b in list_block]
        
        print('[SUCCESS] all preview trajectory generated')
        
        fig = experiment.block.plot(trajectory)
        plt.show()
    
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
        
        
if __name__ == "__main__":
  
    # start the app
    app = QApplication(sys.argv)
    widget = main_window()
    widget.show()
    sys.exit(app.exec_())
    
    
