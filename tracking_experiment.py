import sys
import os 
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.uic import loadUi

from trajectory_lib import trace, segment, tool
from matplotlib import pyplot as plt
import numpy as np
import random

# Main windows 
class main_window(QMainWindow):
    # initiate the window
    def __init__(self):
        # superclass and load gui from designer 
        super(main_window, self).__init__()
        
        loadUi(os.getcwd() + '\\gui\\tracking_experiment_main_window.ui', self)
        
        # internal state
        self.option = None
        self.trajectory = []
        self.parameter = []
        
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
                #tool.write_to_csv(name, self.option[0], header = ["Ramp", "Parameter"])
                #tool.write_to_csv(name, self.option[0], header = ["Chirp", "Parameter"])
                
                # write the trajectories
                for k, X in enumerate(self.trajectory):
                    name = target + "//Block_" + str(k) + ".csv"
                    print(name)
                    tool.write_to_csv(name, X, header = ["cue", "event"])
                
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
            
            # Ramp
            self.number_cue.setValue(2*option['cue'])
            self.cue_holding_time.setValue(option['hold_cue'])
            self.cue_return_time.setValue(option['after_cue'])
            self.cue_min_time.setValue(option['occ_cue'][0])
            self.cue_max_time.setValue(option['occ_cue'][1])
            self.max_amplitude.setValue(option['max_amplitude'])
            
            # Chirp
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
        ramp_option = {}
        chirp_option = {}
        
        # Ramp
        ramp_option['slope'] = eval(self.Ramp_Slope.text())
        ramp_option['level'] = eval(self.Ramp_Level.text())
        p = [self.Ramp_Min_Pause_Time.value(), self.Ramp_Max_Pause_Time.value()]
        ramp_option['pause'] = sorted(p)
        ramp_option['plateau'] = self.Ramp_Plateau_Time.value()
        ramp_option['repetition'] = self.Ramp_Repetition.value()
        ramp_option['randomise'] = self.Ramp_Order.isChecked()
        
        # Chirp
        chirp_option['frequency'] = [0, self.Max_Frequency.value()]
        chirp_option['start'] = self.Chirp_Start_Time.value()
        chirp_option['ramp'] = self.Chirp_Ramp_Time.value()
        chirp_option['plateau'] = self.Chirp_Plateau_Time.value()
        chirp_option['amplitude'] = self.Chirp_Max_Amplitude.value()
        chirp_option['repetition'] = self.Chirp_Repetition.value()
        
        return ramp_option, chirp_option
    
    @pyqtSlot()
    def preview(self):
        print('retriving block and trajectory options')
        #created an option dictionary option
        ramp_option, chirp_option = self.get_option()
        print(ramp_option)
        print(chirp_option)
        
        print('generating preview trajectory')
        #one instance of each block
        ramp = trace.trapezium(ramp_option['slope'], ramp_option['level'], randomise = ramp_option['randomise'])
        x, _ = ramp.bind(t_pause = ramp_option['pause'], t_plateau = ramp_option['plateau'])
        tool.plot_trajectory(x)
        
        chirp = trace.ramp(level = chirp_option['frequency'], randomise = False, n_instance = 1)
        f = chirp.bind(t_start = chirp_option['start'], t_transition = chirp_option['ramp'], t_plateau = chirp_option['plateau'])
        w = tool.frequency_trajectory_to_chirp(f, A = chirp_option['amplitude']) 
        tool.plot_trajectory(w)
        plt.show()

        print('[SUCCESS] all preview trajectory generated')
        
    @pyqtSlot()
    def generate(self):
        
        # create an option dictionary option 
        print('retrieving block and trajectory options')
        #created an option dictionary option
        ramp_option, chirp_option = self.get_option()
        self.option = [ramp_option, chirp_option]
        print(ramp_option)
        print(chirp_option)
        
        print('generating trajectory')
        #one instance of each block
        #RAMP
        ramp = trace.trapezium(ramp_option['slope'], ramp_option['level'], randomise = ramp_option['randomise'], n_instance = ramp_option['repetition'])
        x, event = ramp.bind(t_pause = ramp_option['pause'], t_plateau = ramp_option['plateau'])
        self.trajectory += [np.transpose(np.vstack((x, event)))]
        t = tool.measure_time(x)
        self.Ramp_Display.display(tool.convert_sec(t, string = True))
        # parameter list
        
        
        #CHIRP
        chirp = trace.ramp(level = chirp_option['frequency'], randomise = False, n_instance = 1)
        f = chirp.bind(t_start = chirp_option['start'], t_transition = chirp_option['ramp'], t_plateau = chirp_option['plateau'])
        f = np.append(f, segment.line(chirp_option['start']).generate())
        f = np.tile(f, chirp_option['repetition'])
        x = tool.frequency_trajectory_to_chirp(f, A = chirp_option['amplitude']) 
        event = (f[1:] > 0)
        self.trajectory += [np.transpose(np.vstack((x, event)))]
        t = tool.measure_time(x)
        self.Chirp_Display.display(tool.convert_sec(t, string = True))
              
        print('[SUCCESS] all trajectory generated')
        
        
        
if __name__ == "__main__":  
    # start the app
    app = QApplication(sys.argv)
    widget = main_window()
    widget.show()
    sys.exit(app.exec_())








