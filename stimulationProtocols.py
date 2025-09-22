####################################################################################################
#defines different stimulation protocols: ELID (rising frequencies), 2Hz, recovery cycle protocols 
#with different background frequencies, noise or different distances between extra pulses, double 
#pulse protocol with 20 ms or 50 ms distance between pulses
#author: A. Maxion, 2025
####################################################################################################

import numpy as np

# definition of stimulation protocols
def setStimulationProtocol(prot):
    i=0
    vec = []
    
    if prot==11:#elID with recovery
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
        for i in range(1,16):
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

    elif prot=="DP":#old double pulse, i.e. recovery cycle protocol
        #20 pulses at 0.25 Hz -> one pulse every 4 seconds
        #to stabilize latency
        offset=0
        numberPrevPulses=100
        for i in range(1,numberPrevPulses+1):
            vec.append(offset+i*4)
        lastPulse=offset+numberPrevPulses*4
        extras=[2, 1, 0.5, 0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02]#distance to next regular puls
        numReg=30#number of regular pulses
        for e in extras:
            #one extra pulse
            vec.append(lastPulse+4-e)
            #regular pulses
            for i in range(1,numReg+1):
                vec.append(lastPulse+i*4)
            lastPulse=lastPulse+numReg*4
    
    elif prot=="DPNew":#new double pulse protocol, distance between pulses 50ms
        numberOfPulses=20
        for i in range(1,numberOfPulses+1):
            vec.append(i*16)
            vec.append(i*16+0.05)
        lastPulse=numberOfPulses*16+0.05
        numberOfPulses=30
        for i in range(1,numberOfPulses+1):
            vec.append(lastPulse+i*8)
            vec.append(lastPulse+i*8+0.05)
        lastPulse+=numberOfPulses*8+0.05
        numberOfPulses=30
        for i in range(1,numberOfPulses+1):
            vec.append(lastPulse+i*6)
            vec.append(lastPulse+i*6+0.05)
        lastPulse+=numberOfPulses*6+0.05
        numberOfPulses=40
        for i in range(1,numberOfPulses+1):
            vec.append(lastPulse+i*4)
            vec.append(lastPulse+i*4+0.05)
        lastPulse+=numberOfPulses*4+0.05
        numberOfPulses=80
        for i in range(1,numberOfPulses+1):
            vec.append(lastPulse+i*2)
            vec.append(lastPulse+i*2+0.05)
        lastPulse+=numberOfPulses*2+0.05
        numberOfPulses=100
        for i in range(1,numberOfPulses+1):
            vec.append(lastPulse+i*1.5)
            vec.append(lastPulse+i*1.5+0.05)
        lastPulse+=numberOfPulses*1.5+0.05
        numberOfPulses=150
        for i in range(1,numberOfPulses+1):
            vec.append(lastPulse+i*1)
            vec.append(lastPulse+i*1+0.05)
        lastPulse+=numberOfPulses*1+0.05

    elif prot=="DPNew2":#new double pulse protocol, distance between pulses 20ms
        numberOfPulses=20
        for i in range(1,numberOfPulses+1):
            vec.append(i*16)
            vec.append(i*16+0.02)
        lastPulse=numberOfPulses*16
        numberOfPulses=30
        for i in range(1,numberOfPulses+1):
            vec.append(lastPulse+i*8)
            vec.append(lastPulse+i*8+0.02)
        lastPulse+=numberOfPulses*8
        numberOfPulses=30
        for i in range(1,numberOfPulses+1):
            vec.append(lastPulse+i*6)
            vec.append(lastPulse+i*6+0.02)
        lastPulse+=numberOfPulses*6
        numberOfPulses=40
        for i in range(1,numberOfPulses+1):
            vec.append(lastPulse+i*4)
            vec.append(lastPulse+i*4+0.02)
        lastPulse+=numberOfPulses*4
        numberOfPulses=80
        for i in range(1,numberOfPulses+1):
            vec.append(lastPulse+i*2)
            vec.append(lastPulse+i*2+0.02)
        lastPulse+=numberOfPulses*2
        numberOfPulses=100
        for i in range(1,numberOfPulses+1):
            vec.append(lastPulse+i*1.5)
            vec.append(lastPulse+i*1.5+0.02)
        lastPulse+=numberOfPulses*1.5
        numberOfPulses=150
        for i in range(1,numberOfPulses+1):
            vec.append(lastPulse+i*1)
            vec.append(lastPulse+i*1+0.02)
        lastPulse+=numberOfPulses*1

    return vec

#recovery cycle protocol for different background frequencies
#freq: background frequency
def protDP(freq):
    #100 pulses at 0.25 Hz -> one pulse every 4 seconds
    #to stabilize latency
    offset=0
    vec=[]
    numberPrevPulses=100
    for i in range(1,numberPrevPulses+1):
        vec.append(offset+i*freq)
    lastPulse=offset+numberPrevPulses*freq
    extras=[2, 1, 0.5, 0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02]#distance to next regular puls
    numReg=30#number of regular pulses
    for e in extras:
        #one extra pulse
        vec.append(lastPulse+freq-e)
        #regular pulses
        for i in range(1,numReg+1):
            vec.append(lastPulse+i*freq)
        lastPulse=lastPulse+numReg*freq
    return vec        

#recovery cycle protocol with aded noise to the extra pulses
def protRecNoise():
    #100 pulses at 0.25 Hz -> one pulse every 4 seconds
    #to stabilize latency
    offset=0
    numberPrevPulses=100
    vec=[]
    for i in range(1,numberPrevPulses+1):
        vec.append(offset+i*4)
    lastPulse=offset+numberPrevPulses*4
    extras=[2, 1, 0.5, 0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02]#distance to next regular puls
    # add noise
    noise=[]
    for e in extras:
        noise.append(np.random.normal(e, e*0.2))
    
    extras=noise
    extras2=extras
    
    numReg=30#number of regular pulses
    for e in extras:
        #one extra pulse
        vec.append(lastPulse+4-e)
        #regular pulses
        for i in range(1,numReg+1):
            vec.append(lastPulse+i*4)
        lastPulse=lastPulse+numReg*4
    
    return vec

#recovery cycle protocol with different distances for extra pulses
def protRecBetween():   
    #20 pulses at 0.25 Hz -> one pulse every 4 seconds
    #to stabilize latency
    offset=0
    numberPrevPulses=100
    vec=[]
    for i in range(1,numberPrevPulses+1):
        vec.append(offset+i*4)
    lastPulse=offset+numberPrevPulses*4
    #extras=[2, 1, 0.5, 0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02]#distance to next regular puls
    extras=[1.5, 0.75, 0.375, 0.2, 0.125, 0.075, 0.045, 0.035, 0.025, 0.015]
    numReg=30#number of regular pulses
    for e in extras:
        #one extra pulse
        vec.append(lastPulse+4-e)
        #regular pulses
        for i in range(1,numReg+1):
            vec.append(lastPulse+i*4)
        lastPulse=lastPulse+numReg*4
    return vec



