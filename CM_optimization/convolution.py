#import scipy.signal as signal
#import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import scipy.stats as stats
import time
from scipy.signal import fftconvolve

def memory(x, y, params):
    a, b, c=params
    res=a-b*x-c*y
    #if res <0:
    #    res=0
    #res=a*np.exp(-b*x)-c*y#exponential decay instead of linear, so contributions from dense pulse trains saturate instead of accumulating unboundedly - tried, grid search showed it's worse overall (2.49 vs 2.30)
    res=np.maximum(res, 0)#elementwise-safe clip: works for scalars (clacLatency/convolution) and arrays (convolution_vec)
    return res

#candidate replacement for memory(): genuine positive feedback from accumulated latency
#(more prior slowing -> more future contribution), log-capped so it doesn't diverge over a
#long train. c>=0 required (see particleSwarm2GEPSO.py's upper(2), widened from 0.01 to 1
#to let this term actually have a visible effect - the old -c*y form's c<=0.01 bound couldn't
#express a positive-feedback contribution at all, regardless of sign convention)
def memory_feedback(x, y, params):
    
    a, b, c=params
    res=a-b*x+c*np.log1p(y)
    res=np.maximum(res, 0)

    return res

#2D nonlinear-stage memory function, matching _Final_2D_RecoveryCycle2-vectorized.ipynb's m(x_arr, y_arr)
#params: d, e1, e2, f2, g, h, q - free parameters for the ISI<0.5s branch, optimized in the nonlinear stage
#a, b, c: frozen from the best linear-stage fit (opt-Linear-Convo-CM-run8, score 2.2902)
#x: inter-stimulus interval (s), y: pre-existing slowing/PA
#works for both scalar x (old-style clacLatency) and array x (convolution_vec)
def memory_2D(x, y, params):
    d, e1, e2, f2, g, h, q = params
    a = 0.13641201102376302 #frozen: best 'a' from opt-Linear-Convo-CM-run15+fb (memory_feedback formula)
    b = 0.005609318714023002 #frozen: best 'b' from opt-Linear-Convo-CM-run15+fb
    c = 0.07467626884305203 #frozen: best 'c' from opt-Linear-Convo-CM-run15+fb (now meaningfully nonzero)

    linear_branch = np.maximum(a - b*x + c*np.log1p(np.maximum(y, 0)), 0)#clip negative y (possible from the unbounded nonlinear branch) before log1p, which is only valid for y>-1

    y_floored = np.maximum(y, 0.5)#below 0.5, PA is treated as exactly 0.5 in the log term
    log_arg = np.maximum(q*y_floored, 1e-12)#numerical safety net for q=0 (a valid boundary value PSO can land on)
    nonlinear_branch = np.exp(-d*(x-e1)) - np.log(log_arg)*h*np.exp(-f2*(x-e2)) + g

    return np.where(x >= 0.5, linear_branch, nonlinear_branch)

#for 2d memory function
#calculate latency with convolution
def clacLatency(stim, params):
    latency = []
    for i in range(len(stim)):
        summe=0
        for k in range(i):
            m=memory(stim[i]-stim[k],latency[k], params)
            summe=summe+m
        latency.append(summe)

    return latency

#for 2d memory function
def convolution(stim, memoryFunc):
    #start timer
    tic = time.perf_counter()
    
    latency = []
    for i in range(len(stim)):
        #print("i=",i)
        summe=0
        for k in range(i):
            #print("i-k=",stim[i]-stim[k])
            #print("latency[k]=", latency[k])
            m=memoryFunc(stim[i]-stim[k],latency[k])
            #print("m=",m)
            summe=summe+m
        latency.append(summe)
    toc = time.perf_counter()
    print(f"Simulation time: {(toc - tic):0.10f} s")
    return latency

def convolution_vec(stim, memoryFuncVec):
    """
    Stim is a 1D array (or list) of times.
    memoryFuncVec is a vectorized function returning an array of outputs 
    given arrays (x_arr, y_arr).
    """
    #start timer
    tic = time.perf_counter()
    
    stim = np.asarray(stim, dtype=float)
    n = len(stim)
    latency = np.zeros(n, dtype=float)

    for i in range(n):
        # For each i, we do a "bulk" computation over k=0..i-1
        x_diff = stim[i] - stim[:i]     # shape (i,)
        lat_k  = latency[:i]           # shape (i,)
        
        vals = memoryFuncVec(x_diff, lat_k)  # shape (i,)
        latency[i] = np.sum(vals)

    toc = time.perf_counter()
    #print(f"Simulation time: {(toc - tic)/60:0.10f} min")

    return latency

#for 1d memory function
#calculates the convolution of impulses and f
#impulses: numpy array with times of impulses
#dt: stepsize 
#end: endtime for impulses
#f: function to be convolved with
#l: length for function
#plotTitle: title for plot
def delay(impulses, dt, end, f, plotTitle="Convolution", plot=False):
    #start timer
    tic = time.perf_counter()
    
    #calculate convolution
    impulses_array = np.array(impulses, dtype=float)
    
    #Indizes berechnen
    i = np.rint(impulses_array / dt).astype(int)
    
    #Impulssignal anlegen
    Nt = int(round(end/dt))
    imp = np.zeros(Nt, dtype=float)
    imp[i] = 1.0  # setze Impulse
    
    #x-Achse definieren + f(x)
    x = np.arange(0, end, dt)
    # Wenn f vektorfähig:
    func = f(x)
    
    # Faltung ausführen (FFT oder normal)
    # conv = np.convolve(func, imp, mode='full')
    conv = fftconvolve(func, imp, mode='full')
    
    #highlight_indices
    highlight_indices = np.clip(i, 0, len(conv)-1)
    
    toc = time.perf_counter()
    print(f"Simulation time: {(toc - tic):0.10f} s")

    #plotten
    if plot:
        plt.rcParams.update({'font.size': 16})
        plt.figure(figsize=(15, 2)) 
        plt.plot(x,imp, marker='.')
        plt.title("Stimulation")
        plt.show()

        x2=np.arange(0,len(func))
        #x2=np.delete(x2,-1)
        
        plt.figure(figsize=(15, 2)) 
        plt.plot(x2,func, marker='.', markersize=1, linestyle="none")
        #plt.title("Memory Function")
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

def multi_impulse_signal(shape, positions, dtype=float):
    """Erzeugt ein Array der gegebenen Form 'shape' mit Impulsen
    (1en) an den in 'positions' angegebenen Stellen."""
    out = np.zeros(shape, dtype=dtype)
    for pos in positions:
        # pos sollte ein Integer sein (ggf. int(...) nehmen)
        out[int(pos)] = 1
    return out

