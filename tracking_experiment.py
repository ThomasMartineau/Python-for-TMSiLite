import sys
import os 
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.uic import loadUi

from trajectory_lib import trace, segment, tool
from matplotlib import pyplot as plt
import numpy as np

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
        self.table = None
        
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
                if not self.trajectory: self.generate() 
                    
                # add the config file
                name = target + "//Config.csv"
                
                # config for the ramps
                tool.write_to_csv(name, self.option)
            
                # add an event marker file
                name = target + "//Table.csv"
                tool.write_to_csv(name, self.table, header = ["Event", "Slope", "Level"])
                
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
                      
            # Ramp
            self.Ramp_Slope.setText(str(option['ramp_slope']))
            self.Ramp_Level.setText(str(option['ramp_level']))
            self.Ramp_Min_Pause_Time.setValue(option['ramp_pause'][0])
            self.Ramp_Max_Pause_Time.setValue(option['ramp_pause'][1])
            self.Ramp_Plateau_Time.setValue(option['ramp_plateau'])
            self.Ramp_Repetition.setValue(option['ramp_repetition'])
            self.Ramp_Order.setChecked(option['ramp_randomise'])
            
            # Chirp
            self.Max_Frequency.setValue(option['chirp_frequency'][0])
            self.Chirp_Start_Time.setValue(option['chirp_start'])
            self.Chirp_Ramp_Time.setValue(option['chirp_ramp'])
            self.Chirp_Plateau_Time.setValue(option['chirp_plateau'])
            self.Chirp_Max_Amplitude.setValue(option['chirp_amplitude'])
            self.Chirp_Repetition.setValue(option['chirp_repetition'])
            
            print("[SUCCESS] all option loaded")

    def get_option(self):
        print('retrieving block and trajectory options')
        
        # empty dictionary
        option = {}
        
        # Ramp
        option['ramp_slope'] = eval(self.Ramp_Slope.text())
        option['ramp_level'] = eval(self.Ramp_Level.text())
        p = [self.Ramp_Min_Pause_Time.value(), self.Ramp_Max_Pause_Time.value()]
        option['ramp_pause'] = sorted(p)
        option['ramp_plateau'] = self.Ramp_Plateau_Time.value()
        option['ramp_repetition'] = self.Ramp_Repetition.value()
        option['ramp_randomise'] = self.Ramp_Order.isChecked()
        
        # Chirp
        option['chirp_frequency'] = [0, self.Max_Frequency.value()]
        option['chirp_start'] = self.Chirp_Start_Time.value()
        option['chirp_ramp'] = self.Chirp_Ramp_Time.value()
        option['chirp_plateau'] = self.Chirp_Plateau_Time.value()
        option['chirp_amplitude'] = self.Chirp_Max_Amplitude.value()
        option['chirp_repetition'] = self.Chirp_Repetition.value()
        
        self.option = option
        print(option)
        
        return option
    
    @pyqtSlot()
    def preview(self):
        #created an option dictionary option
        option = self.get_option()
        
        print('generating preview trajectory')
        #one instance of each block
        ramp = trace.trapezium(option['ramp_slope'], option['ramp_level'], randomise = option['ramp_randomise'])
        x, _ = ramp.bind(t_pause = option['ramp_pause'], t_plateau = option['ramp_plateau'])
        tool.plot_trajectory(x)
        
        chirp = trace.ramp(level = option['chirp_frequency'], randomise = False, n_instance = 1)
        f = chirp.bind(t_start = option['chirp_start'], t_transition = option['chirp_ramp'], t_plateau = option['chirp_plateau'])
        w = tool.frequency_trajectory_to_chirp(f, A = option['chirp_amplitude']) 
        tool.plot_trajectory(w)
        plt.show()

        print('[SUCCESS] all preview trajectory generated')
        
    @pyqtSlot()
    def generate(self):
        #created an option dictionary option
        option = self.get_option()        
       
        print('generating trajectory')
        #one instance of each block
        #RAMP
        ramp = trace.trapezium(option['ramp_slope'], option['ramp_level'], randomise = option['ramp_randomise'], n_instance = option['ramp_repetition'])
        self.table = ramp.table
        x, event = ramp.bind(t_pause = option['ramp_pause'], t_plateau = option['ramp_plateau'])
        self.trajectory += [np.transpose(np.vstack((x, event)))]
        t = tool.measure_time(x)
        self.Ramp_Display.display(tool.convert_sec(t, string = True))
        
        
        #CHIRP
        chirp = trace.ramp(level = option['chirp_frequency'], randomise = False, n_instance = 1)
        f = chirp.bind(t_start = option['chirp_start'], t_transition = option['chirp_ramp'], t_plateau = option['chirp_plateau'])
        f = np.append(f, segment.line(option['chirp_start']).generate())
        f = np.tile(f, option['chirp_repetition'])
        x = tool.frequency_trajectory_to_chirp(f, A = option['chirp_amplitude']) 
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








