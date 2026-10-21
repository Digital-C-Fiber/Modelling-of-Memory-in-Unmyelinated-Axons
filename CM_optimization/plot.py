from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from ast import literal_eval
import re
import dataProcessing
from matplotlib.colors import Normalize
import matplotlib.cm as cm


#parse a position string, stripping numpy's "np.float64(...)" repr wrapper (numpy>=2.0) before literal_eval
def parsePosition(s):
    return literal_eval(re.sub(r'np\.float64\(([^)]+)\)', r'\1', s))

def plotLatency(data_aps, data_stim, norm=False):
    l = dataProcessing.calculateLatency(data_aps, data_stim, norm)
       
    if len(l)>0:
        plt.figure(figsize=(15,5))
        plt.scatter(l[:,0],l[:,1])
        plt.xlabel('time (s)')
        plt.ylabel('latency (ms)')
        plt.title('Latency')
        plt.show()


#get lower bound for channel
def lower(ion):
    return 0#because negative values don't make sense
    '''
    if ion==gKdr or ion==gNav18:
        return ion-2*ion
    else:
        return ion-4*ion
    '''
    #return ion-(0.5*ion)
    #return -4.5#beale
    #return -2*math.pi#mishra bird
    #return -10#holder
    #return -512#eggholder
    #return -100#schaffer, easom


#get upper bound for channel
def upper(ion):
    gPump=0.0047891 
    gNav17=0.10664 
    gNav18=0.24271 
    gNav19=9.4779e-05 
    gKs=0.0069733 
    gKf=0.012756 
    gH=0.0025377 
    gKdr=0.018002 
    gKna=0.00042
    
    if ion==gKdr or ion==gNav18:
        return 2*ion
    else:
        return 4*ion
    
    #return ion+(0.5*ion)
    #return 4.5#beale
    #return 2*math.pi#mishra bird
    #return 10#holder
    #return 512#eggholder
    #return 100#schaffer, easom

#plot particle positions and scores
def plotParticles(dimension, num_particles, num_iterations, name):
    gPump=0.0047891 
    gNav17=0.10664 
    gNav18=0.24271 
    gNav19=9.4779e-05 
    gKs=0.0069733 
    gKf=0.012756 
    gH=0.0025377 
    gKdr=0.018002 
    gKna=0.00042
    
    channel_names=["Pump", "Nav17", "Nav18", "Nav19", "Ks", "Kf", "h", "Kdr", "Kna"]
    ions=[gPump, gNav17, gNav18, gNav19, gKs, gKf, gH, gKdr, gKna]
    
    '''
    colors=['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                      'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                      'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
    '''
    
    #get particles 
    for j in range(dimension):
        for i in range(num_particles):
            filename='Results/'+str(name)+'/'+str(name)+'particle'+str(i)+'.csv'
            data = pd.read_csv(filename)

            data['Position'] = data['Position'].apply(parsePosition)#make string to list
            
            #weights = np.arange(1, len(data["Position"])+1)
            #plt.scatter(data["Score"], data["Position"].apply(lambda x: x[j]), marker='.', c=weights, cmap=colors[i])
            
            #plt.plot(data["Score"], data["Position"].apply(lambda x: x[j]), marker='.')
            plt.plot(data["Position"].apply(lambda x: x[j]), data["Score"], marker='.')
        
        plt.xlim(lower(ions[j]), upper(ions[j]))
        #plt.xlim(0,2)
        plt.title(channel_names[j])
        plt.ylabel("Score")
        plt.xlabel("conduction")
        plt.show()

    
def plotParticles2D(dimension, num_particles, num_iterations, name, showInf, channel_names=["a", "b", "c"], scoreCutoff=float('inf')):
    
    
    filename='Results/'+str(name)+'/'+str(name)+'_bestParticles.csv'
    dataBest = pd.read_csv(filename)
    dataBest['Position'] = dataBest['Position'].apply(parsePosition)#make string to list

    #get particles 
    allData=[]
    for i in range(num_particles):
        filename='Results/'+str(name)+'/'+str(name)+'particle'+str(i)+'.csv'
        data = pd.read_csv(filename)
        data['Position'] = data['Position'].apply(parsePosition)#make string to list
        data=data[0:num_iterations]
        
        if scoreCutoff!=float('inf'):
            data = data[data['Score'] < scoreCutoff]#only data with score < scoreCutoff
            data=data.reset_index()
        
        if showInf:
            data.replace([np.inf, -np.inf], 100, inplace=True)
        allData.append(data)
        
    figure, axis = plt.subplots(dimension, dimension, figsize=(25, 25))    
    maxScore=0
    # getting the original colormap using cm.get_cmap() function
    orig_map=plt.colormaps['YlGnBu']
    # reversing the original colormap using reversed() function
    reversed_map = orig_map.reversed()
    
    for p1 in range(dimension):
        for p2 in range(dimension):
            dataHist=[]
            for i in range(num_particles):
                if p2<p1:
                    im=axis[p1,p2].scatter(allData[i]["Position"].apply(lambda x: x[p2]), allData[i]["Position"].apply(lambda x: x[p1]), c=allData[i]["Score"], cmap=reversed_map, marker=".")
                    
                    #find max score
                    maxi = np.where(np.isinf(allData[i]["Score"]),-np.inf,allData[i]["Score"]).argmax()
                    if maxScore<maxi:
                        maxScore=maxi

                    dbLength=len(dataBest)
                    axis[p1,p2].plot(dataBest["Position"][dbLength-1][p2], dataBest["Position"][dbLength-1][p1], c="Red", zorder=100, markersize=10, marker="*")
                elif p1==p2:
                    dataHist.append(allData[i]["Position"].apply(lambda x: x[p1]))

            if p1==p2:
                axis[p1,p2].hist(dataHist)
                
            axis[p1,0].set_ylabel(channel_names[p1])
            axis[dimension-1,p2].set_xlabel(channel_names[p2])
    
    if maxScore>scoreCutoff:
        maxScore=scoreCutoff
    print(f'MaxScore={maxScore}')    
    normalizer=Normalize(0,maxScore)
    im=cm.ScalarMappable(norm=normalizer, cmap=reversed_map)
    figure.colorbar(im, ax=axis.ravel().tolist())
    
    #figure.subplots_adjust(right=0.8)
    #cbar_ax = figure.add_axes([0.85, 0.15, 0.05, 0.7])
    #figure.colorbar(im, cax=cbar_ax)
#plots 2d marginals of particles as a heatmap, and 1d marginals as histogram 
#dimension: number of dimensions of particle
#num_particles: number of particles
#num_iterations: number of iterations
#name: filename 
#replaceInf: replace infinite values with number
#scoreCutoff: only plot particles with scores below cutoff
#nBins: number of bins shown in heatmap
def plotParticles2DMarginal(dimension, num_particles, num_iterations, name, replaceInf=float('inf'), scoreCutoff=float('inf'), nBins=10):
    gPump=0.0047891 
    gNav17=0.10664 
    gNav18=0.24271 
    gNav19=9.4779e-05 
    gKs=0.0069733 
    gKf=0.012756 
    gH=0.0025377 
    gKdr=0.018002 
    gKna=0.00042
    
    channel_names=["Pump", "Nav17", "Nav18", "Nav19", "Ks", "Kf", "h", "Kdr", "Kna"]
    ions=[gPump, gNav17, gNav18, gNav19, gKs, gKf, gH, gKdr, gKna]
    
    #get best particles
    filename='Results/'+str(name)+'/'+str(name)+'_bestParticles.csv'
    dataBest = pd.read_csv(filename)
    dataBest['Position'] = dataBest['Position'].apply(parsePosition)#make string to list
    
    #get all particles 
    allData=[]
    for i in range(num_particles):
        filename='Results/'+str(name)+'/'+str(name)+'particle'+str(i)+'.csv'
        data = pd.read_csv(filename)
        data['Position'] = data['Position'].apply(parsePosition)#make string to list
        data=data[0:num_iterations]
        
        if scoreCutoff!=float('inf'):
            data = data[data['Score'] < scoreCutoff]#only data with score < scoreCutoff
            data = data.reset_index()
                
        if replaceInf!=float('inf'):
            data.replace([np.inf, -np.inf], replaceInf, inplace=True)#replace infinite values with number
        allData.append(data)
                
    maxScore=0
    # getting the original colormap using cm.get_cmap() function
    orig_map=plt.colormaps['YlGnBu']
    # reversing the original colormap using reversed() function
    reversed_map = orig_map.reversed()
    
    figure, axis = plt.subplots(dimension, dimension, figsize=(25, 25))
    for p1 in range(dimension):
        for p2 in range(dimension):
            dataHist=[]
            
            if p2<p1:
                gridFinal = np.zeros_like(allData[0]["Score"], shape=(nBins+1, nBins+1))
                countFinal = np.zeros_like(allData[0]["Score"], shape=(nBins+1, nBins+1))

                #set step size
                if ions[p1]==gKdr or ions[p1]==gNav18:
                    xstep=ions[p1]*2/nBins
                else:
                    xstep=ions[p1]*4/nBins
                #print(xstep)

                if ions[p2]==gKdr or ions[p2]==gNav18:
                    ystep=ions[p2]*2/nBins
                else:
                    ystep=ions[p2]*4/nBins
                #print(ystep)
 
            for i in range(num_particles):
                if p2<p1:
                    x=allData[i]["Position"].apply(lambda x: x[p1])#Nav17
                    y=allData[i]["Position"].apply(lambda x: x[p2])#pump
                    #print(x)
                    #print(y)
                    
                    #calculate bins
                    xbin = ((x) // xstep).astype(int)
                    ybin = ((y) // ystep).astype(int) 
                    #print(xbin)
                    #print(ybin)
                    
                    grid = np.zeros_like(allData[i]["Score"], shape=(nBins+1, nBins+1))
                    count = np.zeros_like(allData[i]["Score"], shape=(nBins+1, nBins+1))
                    np.add.at(grid, (xbin, ybin), allData[i]["Score"])# add scores
                    #print(grid)
                    np.add.at(count, (xbin, ybin), 1)#number of values in each field
                    #print("Count")
                    #print(count)
                    
                    #print("Grid")
                    #print(grid)
                    gridFinal+=grid
                    countFinal+=count

                elif p1==p2:
                    dataHist.append(allData[i]["Position"].apply(lambda x: x[p1]))
                 
            if p2<p1:              
                gridFinal=gridFinal/countFinal#get mean score
                #print("GridFinal")
                #print(gridFinal)
                
                #print("CountFinal")
                #print(countFinal)
                
                #find max score
                #maxi = np.where(np.isinf(gridFinal),-np.inf, gridFinal).argmax()
                test=np.where(np.isinf(gridFinal),-np.inf, gridFinal)
                maxi = np.nanmax(test)
                #maxi = max(map(max, gridFinal))
                if maxScore<maxi:
                    maxScore=maxi

                axis[p1,p2].imshow(gridFinal, cmap=reversed_map, origin='lower')
                
                #set labels
                if ions[p1]==gKdr or ions[p1]==gNav18:
                    xstepL=ions[p1]*2/5
                else:
                    xstepL=ions[p1]*4/5
                #print(xstep)

                if ions[p2]==gKdr or ions[p2]==gNav18:
                    ystepL=ions[p2]*2/3
                else:
                    ystepL=ions[p2]*4/3
                
                labelX = np.array([round(xstepL*i,4) for i in range(1,6)])
                labelY = np.array([round(ystepL*i,3) for i in range(1,4)])

                axis[p1,p2].set_xticks(np.arange(0,nBins, nBins/3))
                axis[p1,p2].set_yticks(np.arange(0,nBins, nBins/5))
                axis[p1,p2].set_xticklabels(labels=labelY)
                axis[p1,p2].set_yticklabels(labels='')
                #axis[0,p2].set_xticklabels(labels=labelY)
                axis[p1,0].set_yticklabels(labels=labelX)

                #mark best position
                y=dataBest["Position"][num_iterations-1][p2]
                x=dataBest["Position"][num_iterations-1][p1]

                xbin = ((x) // xstep)
                ybin = ((y) // ystep)

                #axis[p1,p2].plot(dataBest["Position"][num_iterations-1][p2], dataBest["Position"][num_iterations-1][p1], c="Red", zorder=100, markersize=10, marker="*")
                axis[p1,p2].plot(ybin, xbin, c="Red", zorder=100, markersize=10, marker="*")
                
            if p1==p2:
                axis[p1,p2].hist(dataHist)
                    
            axis[p1,0].set_ylabel(channel_names[p1])
            axis[dimension-1,p2].set_xlabel(channel_names[p2])
    
    if maxScore>scoreCutoff:
        maxScore=scoreCutoff
    #print(maxScore)    
    normalizer=Normalize(0,maxScore)
    im=cm.ScalarMappable(norm=normalizer, cmap=reversed_map)
    figure.colorbar(im, ax=axis.ravel().tolist())
    
    #figure.subplots_adjust(right=0.8)
    #cbar_ax = figure.add_axes([0.85, 0.15, 0.05, 0.7])
    #figure.colorbar(im, cax=cbar_ax)    
    
def plotParticles2Dindividual(dimension, num_particles, num_iterations, name):
    gPump=0.0047891 
    gNav17=0.10664 
    gNav18=0.24271 
    gNav19=9.4779e-05 
    gKs=0.0069733 
    gKf=0.012756 
    gH=0.0025377 
    gKdr=0.018002 
    gKna=0.00042
    
    channel_names=["Pump", "Nav17", "Nav18", "Nav19", "Ks", "Kf", "h", "Kdr", "Kna"]
    ions=[gPump, gNav17, gNav18, gNav19, gKs, gKf, gH, gKdr, gKna]
    
    '''
    colors=['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                      'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                      'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
    '''

    
    #get particles 
    for i in range(num_particles):
        figure, axis = plt.subplots(dimension, dimension, figsize=(25, 25))
        for p1 in range(dimension):
            for p2 in range(dimension):
                dataHist=[]
                #i=1

                filename='Results/'+str(name)+'/'+str(name)+'particle'+str(i)+'.csv'
                data = pd.read_csv(filename)
                data['Position'] = data['Position'].apply(parsePosition)#make string to list
                data=data[0:num_iterations]

                data.replace([np.inf, -np.inf], 10, inplace=True)
                #print(data["Score"])
                if p2<p1:
                    #im=axis[p1,p2].scatter(data["Position"].apply(lambda x: x[p2]), data["Position"].apply(lambda x: x[p1]), marker='.', c=data["Score"], cmap="seismic")
                    im=axis[p1,p2].scatter(data["Position"].apply(lambda x: x[p2]), data["Position"].apply(lambda x: x[p1]), c=range(num_iterations), cmap="Blues")
                elif p1==p2:
                    #w=upper(ions[p1])/len(data["Score"])
                    #axis[p1,p2].bar(data["Position"].apply(lambda x: x[p1]), data["Score"], width=w, color='c')
                    #b=np.arange(upper(ions[p1]), step=upper(ions[p1])/10)
                    #print(b)
                    dataHist.append(data["Position"].apply(lambda x: x[p1]))
                

                if p1==p2:
                    #print(dataHist)
                    axis[p1,p2].hist(dataHist)


                #axis[p1,p2].set_xlim(lower(ions[p2]), upper(ions[p2]))
                #axis[p1,p2].set_ylim(lower(ions[p1]), upper(ions[p1]))
                #plt.xlim(0,2)
                axis[p1,0].set_ylabel(channel_names[p1])
                axis[dimension-1,p2].set_xlabel(channel_names[p2])
        figure.subplots_adjust(right=0.8)
        cbar_ax = figure.add_axes([0.85, 0.15, 0.05, 0.7])
        figure.colorbar(im, cax=cbar_ax)
        
        
def plotRecoveryCycle(data_aps, data_stim, norm):
    l = dataProcessing.calculateLatency(data_aps, data_stim, norm)
    recoveryCycle=[]
    #extras=[2000, 1750, 1500, 1250, 1000, 750, 500, 250, 150, 100, 75, 50, 40, 30, 20, 10]#distance to next regular puls
    extras=[2000, 1000, 500, 250, 150, 100, 50, 40, 30, 20, 15]#distance to next regular puls
    extrasFinal=[]
    
    numberOfExtra=len(extras)#total number of extra pulses
    numRegPulses=6#number of regular pulses in between extra pulses
    for i in range(numberOfExtra):
        l1=l[20+i*numRegPulses][1]#latency of first extra pulse
        l2=l[21+i*numRegPulses][1]#latency of next regular pulse
        if l1!=-1 and l2!=-1:
            recoveryCycle.append(l2-l1)
            extrasFinal.append(extras[i])
    print(recoveryCycle)
    print(extrasFinal)
    
    plt.plot(extrasFinal, recoveryCycle, marker=".", label="Simulation")
    realDataCMi=[0.324487317, 0.249044214, -0.176721166, 0.452664143, 1.463325936, 1.798056359, 3.110076518, 2.838785715, 3.442295076, 3.763976836,  3.681834103]
    plt.plot(extras, realDataCMi, marker=".", label="CMi")
    realDataCM=[0.240241491, 0.252928694, 0.296115416, 0.546602641, 1.450783851, 2.515537532, 3.780695111, 4.167464007, 4.516383778, 4.916885365, 5.386598886]
    plt.plot(extras, realDataCM, marker=".", label="CM")
    plt.legend()
    plt.xlabel("interspike interval")
    plt.ylabel("slowing/speeding")
    

def plotRealData(filename):
    
    data2, CM, CMi, VHT = dataProcessing.getRealData(filename)

    mean=data2[CMi].mean(axis=1)
    std=data2[CMi].sem(axis=1)

    plt.errorbar(range(len(mean)),mean, std, linestyle='None', marker='.', label="CMi")
    mean=data2[CM].mean(axis=1)
    std=data2[CM].sem(axis=1)
    plt.errorbar(range(len(mean)),mean, std, linestyle='None', marker='.', label="CM")
    mean=data2[VHT].mean(axis=1)
    std=data2[VHT].sem(axis=1)
    plt.errorbar(range(len(mean)),mean, std, linestyle='None', marker='.', label="VHT")
    plt.legend()

#for ELID und Serra
def plotRealSim(filenameReal, data_aps, data_stim, fiberType, norm=False):
    
    data2, CM, CMi, VHT = dataProcessing.getRealData(filenameReal)
    
    #plt.figure(figsize=(15,5))
    
    if fiberType=="CM":
        mean=data2[CM].mean(axis=1)
        std=data2[CM].sem(axis=1)
        #plt.errorbar(data_stim,mean[0:len(data_stim)], std, linestyle='None', marker='.', label="CM", color="black", ecolor="grey")
        plt.errorbar(data_stim,mean[0:len(data_stim)], std[0:len(data_stim)], linestyle='None', marker='.', label="CM", color="black", ecolor="grey")
    elif fiberType=="CMi":
        mean=data2[CMi].mean(axis=1)
        std=data2[CMi].sem(axis=1)
        plt.errorbar(data_stim,mean, std, linestyle='None', marker='.', label="CMi", color="black", ecolor="grey")
    elif fiberType=="VHT":
        mean=data2[VHT].mean(axis=1)
        std=data2[VHT].sem(axis=1)
        plt.errorbar(data_stim,mean, std, linestyle='None', marker='.', label="VHT", color="black", ecolor="grey")
        
    #l = dataProcessing.calculateLatency(data_aps, data_stim, norm)
    l=data_aps
    #print(l)
       
    if len(l)>0:
        plt.scatter(data_stim,l, label="Simulation", color="red", marker='.', zorder=10)
        plt.xlabel('time (s)')
        plt.ylabel('latency (%)')
        plt.title('Latency')
        plt.legend()
        plt.show()
    
def plotRealSimODP(filenameReal, data_sim, norm):
    
    fig, ax=plt.subplots(figsize=(15,5))

    data2, CM, CMi, VHT=dataProcessing.getRealDataODP(filenameReal)

    mean=data2.iloc[CMi].mean()
    sem=data2.iloc[CMi].sem()
    plt.errorbar(range(len(mean)),mean.iloc[::-1], sem.iloc[::-1], linestyle='None', marker='.', label="CMi", color="black", ecolor="grey")

    if data_sim is not None:
        l=data_sim

        recoveryCycle=[]
        for i in range(19,len(l)-2,6):
            recoveryCycle.append(l[i+2]-l[i])

        #print(recoveryCycle)
        plt.scatter(range(len(recoveryCycle)), recoveryCycle[::-1], label="Simulation", color="red")
        ax.set_xticks(range(11))
        labels=["2000", "1000", "500", "250", "150", "100", "50", "40", "30", "20", "15"]
        ax.set_xticklabels(labels[::-1])
        plt.xlabel("interstimulus interval in ms")
        if norm:
            plt.ylabel("slowing in %")
        else:
            plt.ylabel("slowing in ms")
        plt.legend()
                
def plotRealSimFF(data_sim, freq):
    
    fig, ax=plt.subplots(figsize=(15,5))

    #Werte von Vivien
    if freq==10:
        #10HZ,CMi, 2-4-8
        mean=[0.92, 2.26, 4.52]
        sem=[0.56, 0.97, 1.56]
    elif freq==20:
        mean=[1.42,3.07,5.48]
        sem=[0.2, 0.16, 1.35]
    elif freq==50:
        mean=[1.27,2.47,4.57]
        sem=[0.27,0.64,1.78]
    elif freq==100:
        mean=[0.84, 0.91,0.99]
        sem=[0.64,0.69,0.57]
        
    plt.errorbar(range(len(mean)),mean, sem, linestyle='None', marker='.', label="CMi", color="black", ecolor="grey")

    if data_sim is not None:
        l=data_sim

        ff=[l[22]-l[19], l[36]-l[31], l[54]-l[45]]

        plt.scatter(range(len(ff)), ff, label="Simulation", color="red")
    
    ax.set_xticks(range(3))
    labels=[2,4,8]
    ax.set_xticklabels(labels)
    plt.xlabel("number of extra pulses")
    plt.ylabel("slowing in %")
    plt.title("Following Frequencies - "+str(freq)+"Hz")
    plt.legend()
        
        
        
        
        
        