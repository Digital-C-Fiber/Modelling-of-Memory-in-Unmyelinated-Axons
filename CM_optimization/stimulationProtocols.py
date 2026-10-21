#from neuron import h
import numpy as np

def setStimulationProtocol(prot):
    i=0
    vec = []
    if prot == -1:
        for i in range(1,6):
            vec.append(i*8)
        lastPulse=5*8
    elif prot == 0:#Test protocol (10 pulses, 500 ms)
        vec = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5]
    elif prot == 5:#Test protocol (10 pulses, 1000 ms)
        vec = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    elif prot==10:#elID
        #20 pulses at 0.125 Hz -> one pulse every 8 seconds
        for i in range(1,21):
            vec.append(i*8)
        lastPulse=20*8
        #20 pulses at 0.25 Hz -> one pulse every 4 seconds
        for i in range(1,21):
            vec.append(lastPulse+i*4)
        lastPulse=lastPulse+20*4
        #30 pulses at 0.5 Hz -> one pulse every 2 seconds
        for i in range(1,31):
            vec.append(lastPulse+i*2)

    elif prot==11:#elID with recovery
        #20 pulses at 0.125 Hz -> one pulse every 8 seconds
        for i in range(1,21):
            vec.append(i*8)
        lastPulse=20*8
        #20 pulses at 0.25 Hz -> one pulse every 4 seconds
        for i in range(1,21):
            vec.append(lastPulse+i*4)
        lastPulse=lastPulse+20*4
        #30 pulses at 0.5 Hz -> one pulse every 2 seconds
        for i in range(1,31):
            vec.append(lastPulse+i*2)
        lastPulse=lastPulse+30*2
        #10 pulses at 0.25 Hz -> one pulse every 4 seconds
        for i in range(1,11):
            vec.append(lastPulse+i*4)

    elif prot==15:#2 Hz, 3min
        #30 pulses at 2 Hz -> two pulses every second
        offset=0
        for i in range(1,361):
            vec.append(offset+i*0.5)
        lastPulse=360*0.5
        #recovery: 10 pulses at 1/4 Hz -> one pulse every 4 seconds
        for i in range(1,11):
            vec.append(lastPulse+i*4)

    elif prot=="DP":#old Doppelpuls
        #20 pulses at 0.25 Hz -> one pulse every 4 seconds
        #to stabilize latency
        offset=0
        numberPrevPulses=100
        for i in range(1,numberPrevPulses+1):
            vec.append(offset+i*4)
        lastPulse=offset+numberPrevPulses*4
        extras=[2, 1, 0.5, 0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.015]#distance to next regular puls
        numReg=30#number of regular pulses
        for e in extras:
            #one extra pulse
            vec.append(lastPulse+4-e)
            #regular pulses
            for i in range(1,numReg+1):
                vec.append(lastPulse+i*4)
            lastPulse=lastPulse+numReg*4

    elif prot=="FF_5Hz":#following frequency - 5Hz
        offset=0
        numberOfPulses=25
        for i in range(1,numberOfPulses+1):
            vec.append(offset+i*0.2)

    elif prot=="FF_10Hz":#following frequency - 10Hz
        offset=0
        numberOfPulses=25
        for i in range(1,numberOfPulses+1):
            vec.append(offset+i*0.1)

    elif prot=="FF_20Hz":#following frequency - 20Hz
        offset=0
        numberOfPulses=25
        for i in range(1,numberOfPulses+1):
            vec.append(offset+i*0.05)

    elif prot=="FF_50Hz":#following frequency - 50Hz
        numberOfPulses=4
        numberOfBursts=6
        lastPulse=0
        for j in range(1, numberOfBursts+1):
            for i in range(1,numberOfPulses+1):
                vec.append(lastPulse+i*0.02)
            lastPulse=lastPulse+numberOfPulses*0.02+0.18
            
    elif prot=="FF_100Hz":#following frequency - 100Hz
        numberOfPulses=4
        numberOfBursts=6
        lastPulse=0
        for j in range(1, numberOfBursts+1):
            for i in range(1,numberOfPulses+1):
                vec.append(lastPulse+i*0.01)
            lastPulse=lastPulse+numberOfPulses*0.01+0.19
            
        
    elif prot=="FF_5Hz_ADS":#following frequency - indirect
        offset=0
        #20 pulses, 1/4Hz
        numberOfPulses=20
        for i in range(1,numberOfPulses+1):
            vec.append(offset+i*4)
        lastPulse=offset+numberOfPulses*4
        
        nP=[2,4,8]
        for j in range(3):
            #2,4 or 6 pulses, 5Hz
            numberOfPulses=nP[j]
            for i in range(1,numberOfPulses+1):
                vec.append(lastPulse+2-(numberOfPulses-i)*0.2)

            #10 pulses, 1/4Hz
            numberOfPulses=10
            for i in range(1,numberOfPulses+1):
                vec.append(lastPulse+i*4)
            lastPulse=lastPulse+numberOfPulses*4
        
    elif prot=="FF_10Hz_ADS":#following frequency - indirect
        offset=0
        #20 pulses, 1/4Hz
        numberOfPulses=20
        for i in range(1,numberOfPulses+1):
            vec.append(offset+i*4)
        lastPulse=offset+numberOfPulses*4
        
        nP=[2,4,8]
        for j in range(3):
            #2,4 or 6 pulses, 5Hz
            numberOfPulses=nP[j]
            for i in range(1,numberOfPulses+1):
                vec.append(lastPulse+2-(numberOfPulses-i)*0.1)

            #10 pulses, 1/4Hz
            numberOfPulses=10
            for i in range(1,numberOfPulses+1):
                vec.append(lastPulse+i*4)
            lastPulse=lastPulse+numberOfPulses*4

        
    elif prot=="FF_20Hz_ADS":#following frequency - indirect
        offset=0
        #20 pulses, 1/4Hz
        numberOfPulses=20
        for i in range(1,numberOfPulses+1):
            vec.append(offset+i*4)
        lastPulse=offset+numberOfPulses*4
        
        nP=[2,4,8]
        for j in range(3):
            #2,4 or 6 pulses, 5Hz
            numberOfPulses=nP[j]
            for i in range(1,numberOfPulses+1):
                vec.append(lastPulse+2-(numberOfPulses-i)*0.05)

            #10 pulses, 1/4Hz
            numberOfPulses=10
            for i in range(1,numberOfPulses+1):
                vec.append(lastPulse+i*4)
            lastPulse=lastPulse+numberOfPulses*4
        
    elif prot=="FF_50Hz_ADS":#following frequency - indirect
        offset=0
        #20 pulses, 1/4Hz
        numberOfPulses=20
        for i in range(1,numberOfPulses+1):
            vec.append(offset+i*4)
        lastPulse=offset+numberOfPulses*4
        
        nP=[2,4,8]
        for j in range(3):
            #2,4 or 6 pulses, 5Hz
            numberOfPulses=nP[j]
            for i in range(1,numberOfPulses+1):
                vec.append(lastPulse+2-(numberOfPulses-i)*0.02)

            #10 pulses, 1/4Hz
            numberOfPulses=10
            for i in range(1,numberOfPulses+1):
                vec.append(lastPulse+i*4)
            lastPulse=lastPulse+numberOfPulses*4
        
    elif prot=="FF_100Hz_ADS":#following frequency - indirect
        offset=0
        #20 pulses, 1/4Hz
        numberOfPulses=20
        for i in range(1,numberOfPulses+1):
            vec.append(offset+i*4)
        lastPulse=offset+numberOfPulses*4
        
        nP=[2,4,8]
        for j in range(3):
            #2,4 or 6 pulses, 5Hz
            numberOfPulses=nP[j]
            for i in range(1,numberOfPulses+1):
                vec.append(lastPulse+2-(numberOfPulses-i)*0.01)

            #10 pulses, 1/4Hz
            numberOfPulses=10
            for i in range(1,numberOfPulses+1):
                vec.append(lastPulse+i*4)
            lastPulse=lastPulse+numberOfPulses*4

    elif prot=="DP2hz":#Doppelpuls with 2Hz background (period 0.5s), extras down to 5ms
            #800 pulses at 2 Hz -> one pulse every 0.5 seconds
            #to stabilize latency (2Hz needs ~800 to settle; same as evaluateMPI's 2Hz score and run_plot.py)
            offset=0
            #numberPrevPulses=100
            numberPrevPulses=800
            for i in range(1,numberPrevPulses+1):
                #vec.append(offset+i*4)
                vec.append(offset+i*0.5)
            #lastPulse=offset+numberPrevPulses*4
            lastPulse=offset+numberPrevPulses*0.5
            #extras=[2, 1, 0.5, 0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.015, 0.010, 0.005]#distance to next regular puls
            extras=[0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.015, 0.010, 0.005]#distance to next regular puls (only extras < 0.5s fit in the period)
            numReg=30#number of regular pulses
            for e in extras:
                #one extra pulse
                #vec.append(lastPulse+4-e)
                vec.append(lastPulse+0.5-e)
                #regular pulses
                for i in range(1,numReg+1):
                    #vec.append(lastPulse+i*4)
                    vec.append(lastPulse+i*0.5)
                #lastPulse=lastPulse+numReg*4
                lastPulse=lastPulse+numReg*0.5

    return vec



        
        
        