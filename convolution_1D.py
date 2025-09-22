####################################################################################################
#contains definjtion of memory function for 1D model and convolution function
#author: A. Maxion, 2025
####################################################################################################

import matplotlib.pyplot as plt
import numpy as np
import time
from scipy.signal import fftconvolve

#vectorized memory function
#x is a numpy array
def memory_1D(x):

    # constants
    c = 12
    d = 4.690202311153471
    e_ = 1.5871555373943715
    f_ = 0.3251898090248414

    # for the linear part
    x1, y1 = 0,  0.19
    x2, y2 = 200, 0
    m = (y1 - y2) / (x1 - x2)
    b = (x1 * y2 - x2 * y1) / (x1 - x2)

    # np.piecewise gets:
    # an array x
    # a list of conditions (condlist)
    # a list of functions or values (funclist) 
    # optional default for values that do not fullfill any of the conditions

    return np.piecewise(
        x,
        [x < 0.001,            # condition 1
         (x >= 0.001) & (x < 0.5),  # condition 2
         (x>=0.5) & (x <= 200)],             # condition 3
        [0,                    # value of function for condition 1
         lambda xi: (np.exp(-d*(4*xi - e_)) 
                     - c*np.exp(-(4*xi - e_)/f_)) / 120,  # value of function for condition 1
         lambda xi: m*xi + b,# value of function for condition 1
        0],                   #default
    )



#calculates the convolution of impulses and f for 1d memory function
#impulses: numpy array with times of impulses
#dt: stepsize 
#end: endtime for impulses
#f: memory function
#plotTitle: title for plot
#plot: set true if you want to plot result
def convolution_1D(impulses, dt, end, f, plotTitle="Convolution", plot=False):
    
    #calculate convolution
    impulses_array = np.array(impulses, dtype=float)
    
    #calculate indexes
    i = np.rint(impulses_array / dt).astype(int)
    
    #construct impulse signal
    Nt = int(round(end/dt))
    imp = np.zeros(Nt, dtype=float)
    imp[i] = 1.0  # set impulses
    
    #define axis + f(x)
    x = np.arange(0, end, dt)
    func = f(x)
    
    # do convolution
    conv = fftconvolve(func, imp, mode='full')
    
    highlight_indices = np.clip(i, 0, len(conv)-1)
    
    #plot
    if plot:
        plt.rcParams.update({'font.size': 16})
        plt.figure(figsize=(15, 2)) 
        plt.plot(x,imp, marker='.')
        plt.title("Stimulation")
        plt.show()

        x2=np.arange(0,len(func))
        
        plt.figure(figsize=(15, 2)) 
        plt.plot(x2,func, marker='.', markersize=1, linestyle="none")
        plt.xlabel("inter-stimulus interval (ms)")
        plt.ylabel("latency shift (%)")
        plt.show()

        x2=np.arange(0,len(conv))
        plt.figure(figsize=(15,5)) 
        plt.plot(x2,conv, marker='.', markersize=1, linestyle="none")
        plt.scatter(x2[highlight_indices], conv[highlight_indices], color='red', zorder=3)
        plt.title(plotTitle)
        plt.show()

    return conv[highlight_indices]


    