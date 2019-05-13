#ploting
from matplotlib import pyplot as plt

#number crushing tools
import numpy as np
import scipy.integrate as integrate 

#file management
import csv

#all global constants etc
fs_default = 50

# plotting
def plot_trajectory(x, fs = fs_default): 
    
    t = get_time_min(x)
    f, ax = plt.subplots()
    ax.plot(t,x)
    ax.set_xlabel('time (minutes)')
    ax.set_ylabel('%MVC')
    ax = ax.twinx()
    ax.plot(t[:-1], np.diff(x)*fs, color = 'red')
    ax.set_ylabel('%MVC/s')

# time tool    
# return time vector in minutes
def get_time(x, fs = fs_default):
    n = len(x)
    return np.linspace(0, n/fs, n)

def get_time_min(x, fs = fs_default):
    n = len(x)
    return np.linspace(0, n/(fs*60), n)
    
# measure time
def measure_time(x, fs = fs_default):
    return len(x)/fs

def convert_sec(t, string = False):
    h = t // 3600
    t %= 3600
    m = t // 60
    time = [int(h), int(m), int(t%60)]
    
    if string:
        return ':'.join([str(s) for s in time])
    else:
        return time

# write 
def write_to_csv(name, X, header = None, append = False):
    # comman flow control for saving different data types
    def write_to(target, X, header):
        # get the writing function
        w = csv.writer(target)
        
        if header is not None:
            w.writerow(header)
        
        # for numpy arrays
        if type(X) is np.ndarray:
            # proceed per column 
            for k in range(0, X.shape[0]):
                w.writerow(X[k])
                
        # for lists
        if type(X) is list:
            for x in X:
                w.writerow(x)
        
        # for dictionary types
        elif type(X) is dict:
            for key, value in zip(X.keys(), X.values()):
                # if the value is already a list
                if type(value) is list:
                    row = [key] + value
                else:
                    row = [key, value]
   
                w.writerow(row)

    # flow control to create or edit files
    if not append:
        with open(name, 'w', newline = '') as target:
            write_to(target, X, header)
    else:
         with open(name, 'a', newline = '') as target:
             write_to(target, X, header)

    
         
def read_to_csv(name, output = dict):
    with open(name) as target:
        # get reading function
        rows = csv.reader(target, delimiter = ',')
        
        # in the form of a dictionary
        if output is dict:
            return {r[0]: r[1:] for r in rows}

def clean_csv_dict(X):
    # for every values
    for key, value in zip(X.keys(), X.values()):
        # if value
        if len(value) == 1:
            v = value[0]
            if v == 'False' or v == 'True': X[key] = bool(v)
            else: X[key] = float(value[0]) 
        
        else: X[key] = [float(v) for v in value]
        
    return X

# operation on trajectory      
def frequency_trajectory_to_chirp(f, fs = fs_default, A = 1):
    phi = 2*np.pi*integrate.cumtrapz(f, dx = 1/fs) - np.pi/2
    return A/2*(np.sin(phi) + 1)

#utility function
# return a variable random
def rand_or_det(x, discrete = False):
    #find type
    y = type(x)
    #deterministic
    if  y is int or y is float:
        return x      
    #random between two points
    elif (y is list or y is tuple) and len(x) == 2:
        return rand_interval(x, discrete = discrete)

# return a variable between interval
def rand_interval(x, n = 1, discrete = False):
    # draw random number in the interval
    x = np.random.rand(n)*(x[1] - x[0]) + x[0]

    if discrete:
        return int(x)
    else:  
        return x

def rand_sign(n = 1):
    x = np.random.rand(n)
    if x > 0.5:
        return  1
    else:
        return -1
    
if __name__ == "__main__":
    
    name = "C:\\Users\\Thomas Martineau\\Desktop\\tracking\\Config.csv"
    X = {'test1': 1, 'test2':[2, 3], 'test3': False}
    write_to_csv(name, X)
    X = {'test1': True, 'test2':'x', 'test3': [5,6]}
    write_to_csv(name, X, append = True)
    
#    name = "C:/Users/tlm111/Documents/PhD year 2/repository/Python-for-TMSiLite/test_save//Block_0.csv"
#    X = np.random.rand(4,5)
#    write_to_csv(name, X)

