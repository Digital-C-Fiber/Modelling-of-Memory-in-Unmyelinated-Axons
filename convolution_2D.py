####################################################################################################
#contains definjtion of memory function for 2D model and convolution function
#author: A. Maxion, 2025
####################################################################################################

import numpy as np


#Vectorized memory function
#x_arr, y_arr are NumPy arrays of the same shape
#Returns a NumPy array of the same shape with the elementwise result
def memory_2D(x_arr, y_arr):
    
    # constants
    a,b,c, d, e1, e2, f_, g, h, q = [
        0.22001242418622874, 0.001386879631280578, 0.0, 
        21.800065382804718, 0.10525234957525222, 0.0,
        7.530002307671147, 0.5531734919077812, 2.851578017360972,
        3.485490643651577
    ]

    # Prepare output array
    out = np.empty_like(x_arr, dtype=np.float64)

    # Masks for the piecewise conditions:
    mask_x_small  = (x_arr < 0.5)
    mask_y_large  = (y_arr > 0.5)
    mask1 = mask_x_small & mask_y_large         # x<0.5, y>0.001
    mask2 = mask_x_small & ~mask_y_large        # x<0.5, y<=0.001
    mask3 = ~mask_x_small                       # x>=0.5

    # x < 0.5, y > 0.001
    out[mask1] = (
        np.exp(-d * (x_arr[mask1] - e1))
        - np.log(q * y_arr[mask1]) * h * np.exp(-f_ * (x_arr[mask1] - e2))
        + g
    )
    
    #x < 0.5, y <= 0.001
    out[mask2] = (
        np.exp(-d * (x_arr[mask2] - e1))
        - np.log(q * 0.5) * h * np.exp(-f_ * (x_arr[mask2] - e2))
        + g
    )
    
    # x >= 0.5
    # res = a - b*x - c*y, but clipped to 0 if negative
    tmp = a - b * x_arr[mask3] - c * y_arr[mask3]
    tmp[tmp < 0] = 0
    out[mask3] = tmp

    return out

#calculates convolution of stim and memoryFuncVec
#stim is a 1D array (or list) of times.
#memoryFuncVec is a vectorized function returning an array of outputs 
#returns the calculated latencies
def convolution_vec(stim, memoryFuncVec):
    
    stim = np.asarray(stim, dtype=float)
    n = len(stim)
    latency = np.zeros(n, dtype=float)

    for i in range(n):
        # For each i, we do a "bulk" computation over k=0..i-1
        x_diff = stim[i] - stim[:i]     
        lat_k  = latency[:i]           
        
        vals = memoryFuncVec(x_diff, lat_k)  
        latency[i] = np.sum(vals)
    
    return latency




    