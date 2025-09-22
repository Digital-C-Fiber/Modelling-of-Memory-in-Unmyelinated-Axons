####################################################################################################
#plots output of convolution model for the double pulse protocol and gets recovery cyle data from 
#latencies
#author: A. Maxion, 2025
####################################################################################################

from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
import math
from matplotlib.ticker import FormatStrFormatter
    

#gets recovery cycle data from latencies
#l: latencies
#returns the latencie shifts of the extra pulses in the recovery cycle
def getRecoveryCycle(l):
    recoveryCycle=[]
    numberPrevPulses=100
    numberRegPulses=30
    for i in range(numberPrevPulses-1,len(l)-2,numberRegPulses+1):
        recoveryCycle.append(l[i+2]-l[i])
    return recoveryCycle

#plots data from double pulse protocol with 20 ms distance between pulses
#latency: raw latencies
#savefile: filename of file that saves plot
def plotDoublePulses20(latency, savefile="test"):
    l=latency
    latencyShift=[]
    isi=l[1]-l[0]
    latencyShift.append(isi)
    plt.plot(l[0], isi, marker='.', linestyle='none', color="red", label="in silico")

    currentIndex=0
    for i in range(0, len(l)-1,2):
        if l[i]>=2:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=4:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=6:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=8:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=10:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=12:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=14:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=16:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=18:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=20:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break



    plt.plot(0, 16/360*100, marker='.', linestyle='none', color="black", label="in vivo")
    plt.plot(2, 13/360*100, marker='.', linestyle='none', color="black")
    plt.plot(4, 7/360*100, marker='.', linestyle='none', color="black")
    plt.plot(6, 0/360*100, marker='.', linestyle='none', color="black")
    plt.plot(8, -5/360*100, marker='.', linestyle='none', color="black")
    plt.plot(10, -10/360*100, marker='.', linestyle='none', color="black")
    plt.plot(12, -12/360*100, marker='.', linestyle='none', color="black")
    plt.plot(14, -15/360*100, marker='.', linestyle='none', color="black")
    plt.plot(16, -17.5/360*100, marker='.', linestyle='none', color="black")
    plt.plot(18, -18/360*100, marker='.', linestyle='none', color="black")
    plt.plot(20, -18/360*100, marker='.', linestyle='none', color="black")

    plt.xlabel("pre-existing slowing (%)")
    plt.ylabel("latency shift (%)")
    plt.title("Double Pulses 20 ms distance")
    plt.legend()
    plt.savefig(savefile, dpi=500, bbox_inches='tight')
    plt.show()

        
#plots data from double pulse protocol with 50 ms distance between pulses
#latency: raw latencies
#savefile: filename of file that saves plot        
def plotDoublePulses50(latency, savefile="test"):
    l=latency
    latencyShift=[]
    isi=l[1]-l[0]
    latencyShift.append(isi)
    fig, ax = plt.subplots()
    plt.plot(l[0], isi, marker='.', linestyle='none', color="red", label="in silico")
    plt.plot(0, 9.2/360*100, marker='.', linestyle='none', color="black", label="in vivo")
    currentIndex=0
    
    for i in range(0,len(l)-1,2):
        if l[i]>=1:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break
    plt.plot(1, 7.8/360*100, marker='.', linestyle='none', color="black")

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=5:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break
    plt.plot(5, -3.8/360*100, marker='.', linestyle='none', color="black")

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=10:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break
    plt.plot(10, -17.6/360*100, marker='.', linestyle='none', color="black")

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=15:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break
    plt.plot(15, -29.1/360*100, marker='.', linestyle='none', color="black")

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=20:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break
    plt.plot(20, -37.5/360*100, marker='.', linestyle='none', color="black")

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=25:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break
    plt.plot(25, -40.9/360*100, marker='.', linestyle='none', color="black")

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=30:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break
    plt.plot(30, -41.5/360*100, marker='.', linestyle='none', color="black")

    for i in range(currentIndex, len(l)-1,2):
        if l[i]>=35:
            isi=l[i+1]-l[i]
            latencyShift.append(isi)
            plt.plot(l[i], isi, marker='.', linestyle='none', color="red")
            currentIndex=i
            break
    plt.plot(35, -41.9/360*100, marker='.', linestyle='none', color="black")

    
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    plt.xlabel("pre-existing slowing (%)")
    plt.ylabel("latency shift (%)")
    plt.title("Double Pulses 50 ms distance")
    plt.legend()
    plt.savefig(savefile, dpi=500, bbox_inches='tight')
    plt.show()

    
        