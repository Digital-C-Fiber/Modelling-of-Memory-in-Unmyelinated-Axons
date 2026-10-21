import pandas as pd
import numpy as np
import os


def calculateLatency(data_aps, data_stim, norm=True):
    l = np.zeros((len(data_stim),2))
    j=0
    i=0
    k=0
    while i < len(data_stim):
        if j < len(data_aps):
            point = data_aps[j]-data_stim[i]
            #print(point)
            if point>0 and point < 400:
                l[k][0]=data_stim[i]/1000
                l[k][1]=point
                j=j+1
                i=i+1
                k=k+1
            elif point <0:
                j=j+1
            
            elif point>400:
                l[k][0]=data_stim[i]/1000
                l[k][1]=-1
                i=i+1
                k=k+1
            
        else:
            break
    #normalize
    if norm:
        first=l[0][1]
        j=0
        for i in l:
            l[j][1]=(i[1]/first-1)*100
            j=j+1
    return l

def calculateLatency2(data_aps, data_stim, norm=True):
    l = np.zeros((len(data_stim),2))
    j=0
    i=0
    k=0
    while i < len(data_stim):
        if j < len(data_aps):
            point = data_aps[j]-data_stim[i]
            #print(point)
            if point>0 and point < 400:
                l[k][0]=data_stim[i]/1000
                l[k][1]=point
                j=j+1
                i=i+1
                k=k+1
            elif point <0:
                j=j+1
            
            elif point>400:
                l[k][0]=data_stim[i]/1000
                l[k][1]=-1
                i=i+1
                k=k+1
            
        else:
            break
    #normalize
    if norm:
        first=l[0][1]
        j=0
        for i in l:
            l[j][1]=(i[1]/first-1)*100
            j=j+1
    return l

#for ELID and Serra
def getRealData(filename):
    
    data2 = pd.read_excel(filename, index_col=None, header=4)  

    data2 =data2.drop(1)
    data2 =data2.drop("fiber id",axis=1)

    CM=[]
    CMi=[]
    VHT=[]
    for column in data2:
        #sort cm/cmi
        if data2.at[0,column] == "cm":
            CM.append(column)
        elif data2.at[0,column] == "cmi":
            CMi.append(column)
        elif data2.at[0,column] == "vht":
            VHT.append(column)

    data2= data2.drop(0)

    for column in data2:
        #normalize
        first=data2.at[2,column]
        for row in data2.index:
            data2.at[row,column]=(data2.at[row,column]/first-1)*100

    return data2, CM, CMi, VHT
    
    
def getRealDataODP(filename):
    data = pd.read_excel(filename, index_col=None, header=0)  

    CM=[]
    CMi=[]
    VHT=[]
    for index, row in data.iterrows():
        #sort cm/cmi
        if row['unit class'] == "cm":
            CM.append(index)
        elif row['unit class'] == "cmi":
            CMi.append(index)
        elif row['unit class'] == "vht":
            VHT.append(index)
    
    return data, CM, CMi, VHT
    