import convolution
import dataProcessing
import math
import numpy as np
import scipy.optimize
import csv
import stimulationProtocols

#print in file and on console
def myPrint(text, nr=0, name='test'):
    #print(text)
    with open('Results/'+str(name)+'/Messages/messagesParticle'+str(nr)+'.txt', 'a', newline='') as f:
        csv.writer(f).writerow([text])

#run model and evaluate goodness of fit

#for linear part of memory function    
#run different protocols for one particle
#parameters for particle: a,b,c
#name: name of optimization run
#nr: particle number 
#prot: name or number of protocol to run
def runEvalParticleCM_1(args):
    #a, b1, b2, b3, c, name, nr, prot=args
    a, b, c, name, nr, prot=args
    if prot == 0:
        #ELID
        #myPrint("start ELID, particle "+str(nr),nr, name)       
        scoreELID = evalELIDCM(args)
        myPrint("Score ELID for particle "+str(nr)+": "+str(scoreELID),nr, name)
        return scoreELID
        
    elif prot==1:
        #2Hz - 50 pulses
        #myPrint("start 2Hz, particle "+str(nr),nr, name)
        score=eval2HzCM(args)
        myPrint("Score 2Hz for particle "+str(nr)+": "+str(score),nr, name)
        return score
    
    return float('inf')#should not go here

#for exponential part of memory function
#run different protocols for one particle
#parameters for particle: d,e1,e2,f2,g,h,q
#name: name of optimization run
#nr: particle number
#prot: name or number of protocol to run
def runEvalParticleCM_2(args):
    d, e1, e2, f2, g, h, q, name, nr, prot=args

    if prot==0:
        #RecoveryCycle - old DP
        #myPrint("start Recovery Cycle - old DP: particle "+str(nr),nr, name)
        scoreRecoveryCycle = evalRecoveryCycleCM(args)
        myPrint("Score Recovery Cycle - old DP "+str(scoreRecoveryCycle)+"for particle "+str(nr),nr, name)
        return scoreRecoveryCycle

    '''
    elif prot==1:
        #Following Frequencies 10Hz
        #myPrint("start Following Frequencies 10Hz: particle "+str(nr),nr, name)
        score = ffCMi(args, 10)
        myPrint("Score FF 10Hz for particle "+str(nr)+": "+ str(score),nr, name)
        return score
    
    elif prot==2:
        #Following Frequencies 20Hz
        #myPrint("start Following Frequencies 20Hz: particle "+str(nr),nr, name)
        score = ffCMi(args, 20)
        myPrint("Score FF 20Hz: "+str(score),nr, name)
        return score
    
    elif prot==3:
        #Following Frequencies 50Hz
        #myPrint("start Following Frequencies 50Hz: particle "+str(nr),nr, name)
        score = ffCMi(args, 50)
        myPrint("Score FF 50Hz: "+str(score),nr, name)
        return score
    
    elif prot==4:
        #Following Frequencies 100Hz
        #myPrint("start Following Frequencies 100Hz: particle "+str(nr),nr, name)
        score = ffCMi(args, 100)
        myPrint("Score FF 100Hz: "+str(score),nr, name)
        return score
    '''
    return float('inf')#should not go here

#for linear part of memory function    
#run different protocols for one particle
#parameters for particle: a,b,c
#name: name of optimization run
#nr: particle number 
#prot: name or number of protocol to run
def runEvalParticleCMi_1(args):
    a, b, c, q, name, nr, prot=args
    if prot == 0:
        #ELID
        #myPrint("start ELID, particle "+str(nr),nr, name)       
        scoreELID = evalELIDCMi(args)
        myPrint("Score ELID for particle "+str(nr)+": "+str(scoreELID),nr, name)
        return scoreELID
        
    elif prot==1:
        #2Hz - 50 pulses
        #myPrint("start 2Hz, particle "+str(nr),nr, name)
        score=eval2HzCMi(args)
        myPrint("Score 2Hz for particle "+str(nr)+": "+str(score),nr, name)
        return score/5#because values for 2Hz are 5x higher than for ELID
  
    return float('inf')#should not go here


#calculate score for ELID protocol compared to CM 
#values for comparison from Antonias data
def evalELIDCM(args):
    #a, b1, b2, b3, c, name, nr, prot=args
    a, b, c, name, nr, prot=args
    params=[a, b, c]
    #params=[a, b1, b2, b3, c]

    #stimulation
    data_stim=stimulationProtocols.setStimulationProtocol(11)
    #print(data_stim)

    #relLatency=convolution.clacLatency(data_stim, params)
    #relLatency=convolution.convolution_vec(data_stim, lambda x, y: convolution.memory(x, y, params))
    relLatency=convolution.convolution_vec(data_stim, lambda x, y: convolution.memory_feedback(x, y, params))
    #print(relLatency)

    '''
    dataReal, CM, CMi, VHT=dataProcessing.getRealData("Data/DatenELID_Cleaned.xlsx")
    meanReal=dataReal[CM].mean(axis=1)
    print(meanReal[0:80].to_list())
    '''
    
    meanReal=np.array([0.0, 0.03850589093982677, 0.07124605501607043, 0.07757853281520281, 0.07600287130825792, 0.07373532713241408, 0.08397617383147105, 0.09100039442654825, 0.08332215463977986, 0.08445160632921765, 0.07441428632391389, 0.07794135625305892, 0.07343049897515302, 0.07650294880326186, 0.06164064349149629, 0.05505605811991844, 0.044983691805582905, 0.050008974866817636, 0.040488856456221904, 0.04596559853847812, 0.08890913537464122, 0.14902861065221248, 0.20704738362225436, 0.24361610592810445, 0.2644445609641269, 0.294021289781993, 0.3118093751555461, 0.3201420265779037, 0.3364849884964403, 0.34029152917639194, 0.3526150870814007, 0.35904841674741284, 0.3772468248111523, 0.3910516318565418, 0.3981070500074539, 0.39510272189129014, 0.40911797002594663, 0.40761795906233667, 0.4383239397461736, 0.4706353011333812, 0.5453620924420058, 0.6688057477033836, 0.78722738926406, 0.899535722178005, 0.9988543891264943, 1.0873217079893358, 1.1514665611165222, 1.2265997655809413, 1.3008595662125086, 1.3537149134830786, 1.4028674370414755, 1.4554957278675527, 1.5152900245315168, 1.558895206577986, 1.6145338676284255, 1.6613851486629376, 1.687016060417858, 1.730614171828396, 1.7703128456706194, 1.7936502300246344, 1.82207028873156, 1.8550687801155348, 1.875833660905987, 1.899566769516979, 1.9280424528778581, 1.953970855137985, 1.9707572033315968, 1.986182639382869, 1.9985645540525814, 1.984936959206154, 1.8104810125438637, 1.5223277752999715, 1.318330282088625, 1.1797925159518285, 1.070604718295404, 0.9837811571973202, 0.9081803525360705, 0.8463498815811823, 0.7985493275677009, 0.7623875629105943])
  
    #check if dataframe exists
    if relLatency is not None:
        #mean squared error
        new=(relLatency-meanReal)**2
        #score=new.mean()
        score=new.sum()/(meanReal**2).sum()#NMSE: normalize by ELID's own sum-of-squares ("energy") so both protocols compete on equal footing
        myPrint("Score ADS: "+str(score),nr, name)
        return score

    return float('inf')

#calculate score for ELID protocol compared to CMi
#values for comparison from Antonias data
def evalELIDCMi(args):
    a, b, c, q, name, nr, prot=args
    params=[a, b, c, q]
    
    #stimulation
    data_stim=stimulationProtocols.setStimulationProtocol(11)
    #print(data_stim)
    
    relLatency=convolution.clacLatency(data_stim, params)
    #print(relLatency)
    '''
    dataReal, CM, CMi, VHT=dataProcessing.getRealData("Data/DatenELID_Cleaned.xlsx")
    meanReal=dataReal[CMi].mean(axis=1)
    print(meanReal[0:80].to_list())
    '''
    meanReal=np.array([0.0, 0.2168043212232414, 0.3970060571829007, 0.5540349658504048, 0.6885781533626447, 0.8032844027193146, 0.9117196304540571, 0.986438234776563, 1.0741051303920857, 1.135293355178659, 1.1760705992738687, 1.2331084243279626, 1.302085719410582, 1.327319637994981, 1.3623232653854227, 1.4163388697049508, 1.4543750328984262, 1.4763179440612837, 1.515107571086807, 1.5533952696432196, 1.6751944799062053, 1.8488424973386794, 2.045465522510044, 2.2146046652634994, 2.388350508720996, 2.5362084327438734, 2.6828520603810264, 2.787103314379236, 2.920147763214893, 3.044750557272645, 3.137973432033274, 3.235251377549687, 3.3052717137034193, 3.3748072033833187, 3.4718418916002043, 3.5756401416806582, 3.6302994266833424, 3.699516097336684, 3.7810921751446775, 3.857818987883298, 3.9890177607557167, 4.196408652792864, 4.430237743784279, 4.656335573566752, 4.872679828287096, 5.095224107096609, 5.3056835020177076, 5.489959130591948, 5.6603461940795095, 5.834208841764679, 5.999586739739027, 6.170828641130172, 6.320133811469641, 6.454997150863401, 6.5916506704378435, 6.745803181358596, 6.840385600897128, 6.962445135713928, 7.035837705281438, 7.138095766475927, 7.272605419958719, 7.345382964477305, 7.41635640601462, 7.49877980107264, 7.601544457648437, 7.693398030984106, 7.765001837696804, 7.834580074209285, 7.893948165594124, 7.913462195563328, 7.790423622671782, 7.579331781110489, 7.386340293283807, 7.187070366866892, 7.047323728862597, 6.909471320580622, 6.7801809834641125, 6.693261467778206, 6.600730936496496, 6.517262110465695])
    
    #check if dataframe exists
    if relLatency is not None:
        #mean squared error
        new=(relLatency-meanReal)**2
        score=new.mean()
        myPrint("Score ADS: "+str(score),nr, name)
        return score
    
    return float('inf')


'''
#function to fit curve of recovery/normalization of latency
def funcRec(x,a,b,c):
    return np.exp(-a * x+b) + c

#function to fit curve of rising latency
def func(x,a,b,c):
    return  -np.exp(-a * x+b) + c



#calculate score for ELID protocol compared to CM 
#values for comparison from Antonias data
def evalELIDCM_(args):
    a, b, c, name, nr, prot=args
    params=[a, b, c]
    
    #stimulation
    data_stim=stimulationProtocols.setStimulationProtocol(11)
    #print(data_stim)
    
    relLatency=convolution.clacLatency(data_stim, params)
    #print(relLatency)
    
    #check if dataframe exists
    if relLatency is not None:
        #ADS
        ads1=abs(relLatency[19]-0.042667211836282214)#ADS after 1/8Hz stimulation
        #print(ads1)
        ads2=abs(relLatency[39]-0.431142919493383)#ADS after 1/4Hz stimulation
        #print(ads2)
        ads3=abs(relLatency[69]-1.8545671912198511)#ADS after 1/2Hz stimulation
        #print(ads3)
        ads4=abs(relLatency[79]-0.7035094925966477)#ADS after 1/4Hz stimulation/normalization
        #print(ads4)
        
        #calculate curvature
        try:
            #myPrint(relLatency, name)
            y=relLatency[0:20]
            #myPrint(y, name)
            x=range(len(y))
            params=scipy.optimize.curve_fit(func,  x,  y)
            c1=params[0][0]#curvature after 1/8Hz stimulation
            curvature1=abs(c1-1.367036066580482)
        except:
            myPrint("evalELIDCM: Can not calculate curvature1 for particle "+str(nr),nr, name)
            curvature1=float('inf')
        
        try:
            y=relLatency[20:40]
            #myPrint(y, name)
            x=range(len(y))
            params=scipy.optimize.curve_fit(func,  x,  y)
            c2=params[0][0]#curvature after 1/8Hz stimulation
            curvature2=abs(c2-0.14401807213105303)
        except:
            myPrint("evalELIDCM: Can not calculate curvature2 for particle "+str(nr),nr, name)
            curvature2=float('inf')
        
        try: 
            y=relLatency[40:70]
            #myPrint(y, name)
            x=range(len(y))
            params=scipy.optimize.curve_fit(func,  x,  y)
            c3=params[0][0]#curvature after 1/8Hz stimulation
            curvature3=abs(c3-0.07441074811705436)
        except:
            myPrint("evalELIDCM: Can not calculate curvature3 for particle "+str(nr),nr, name)
            curvature3=float('inf')
        
        try:
            y=relLatency[70:80]
            #myPrint(y, name)
            x=range(len(y))
            params=scipy.optimize.curve_fit(funcRec,  x,  y)
            c4=params[0][0]#curvature after 1/8Hz stimulation
            curvature4=abs(c4-0.2728456712777839)
        except:
            myPrint("evalELIDCM: Can not calculate curvature4 for particle "+str(nr),nr, name)
            curvature4=float('inf')
        
        #print(curvature1)
        #print(curvature2)
        #print(curvature3)
        #print(curvature4)
        scoreCurvature=(curvature1+curvature2+curvature3+curvature4)/4
        score=(ads1+ads2+ads3+ads4)/4
        myPrint("Score ADS: "+str(score),nr, name)
        myPrint("Score Curvature: "+str(scoreCurvature),nr, name)
        return (score+scoreCurvature)/2 
    
    return float('inf')
    
#calculate score for ELID protocol compared to CMi        
def evalELIDCMi_(args):
    a, b, c, name, nr, prot=args
    params=[a, b, c]
    
    #stimulation   
    data_stim=stimulationProtocols.setStimulationProtocol(11)
    
    relLatency=convolution.clacLatency(data_stim,params)
    
    #check if dataframe exists
    if relLatency is not None:
        #ADS
        ads1=abs(relLatency[19]-1.5796529631899026)
        #print(ads1)
        ads2=abs(relLatency[39]-3.899782986912614)
        #print(ads2)
        ads3=abs(relLatency[69]-7.984686271106443)
        #print(ads3)
        ads4=abs(relLatency[79]-6.592790951611635)
        #print(ads4)
        
        #calculate curvature
        try:
            #myPrint(relLatency, name)
            y=relLatency[0:20]
            #myPrint(y, name)
            x=range(len(y))
            params=scipy.optimize.curve_fit(func,  x,  y)
            c1=params[0][0]#curvature after 1/8Hz stimulation
            curvature1=abs(c1-0.12628220956862668)
        except:
            myPrint("evalELIDCMi: Can not calculate curvature1 for particle "+str(nr),nr, name)
            curvature1=float('inf')
        
        try:
            y=relLatency[20:40]
            #myPrint(y, name)
            x=range(len(y))
            params=scipy.optimize.curve_fit(func,  x,  y)
            c2=params[0][0]#curvature after 1/8Hz stimulation
            curvature2=abs(c2-0.06748113483521365)
        except:
            myPrint("evalELIDCMi: Can not calculate curvature2 for particle "+str(nr),nr, name)
            curvature2=float('inf')
        
        try: 
            y=relLatency[40:70]
            #myPrint(y, name)
            x=range(len(y))
            params=scipy.optimize.curve_fit(func,  x,  y)
            c3=params[0][0]#curvature after 1/8Hz stimulation
            curvature3=abs(c3-0.0512067258437281)
        except:
            myPrint("evalELIDCMi: Can not calculate curvature3 for particle "+str(nr),nr, name)
            curvature3=float('inf')
        
        try:
            y=relLatency[70:80]
            #myPrint(y, name)
            x=range(len(y))
            params=scipy.optimize.curve_fit(funcRec,  x,  y)
            c4=params[0][0]#curvature after 1/8Hz stimulation
            curvature4=abs(c4-0.1246833474616466)
        except:
            myPrint("evalELIDCMi: Can not calculate curvature4 for particle "+str(nr),nr, name)
            curvature4=float('inf')
        
        #print(curvature1)
        #print(curvature2)
        #print(curvature3)
        #print(curvature4)
        scoreCurvature=(curvature1+curvature2+curvature3+curvature4)/4
        score=(ads1+ads2+ads3+ads4)/4
        myPrint("Score ADS: "+str(score),nr, name)
        myPrint("Score Curvature: "+str(scoreCurvature),nr, name)
        return (score+scoreCurvature)/2 
    
    return float('inf')     
'''
def eval2HzCM(args):
    a, b, c, name, nr, prot=args
    params=[a, b, c]

    data_stim=stimulationProtocols.setStimulationProtocol(15)

    #relLatency=convolution.clacLatency(data_stim, params)
    #relLatency=convolution.convolution_vec(data_stim, lambda x, y: convolution.memory(x, y, params))
    relLatency=convolution.convolution_vec(data_stim, lambda x, y: convolution.memory_feedback(x, y, params))
    '''
    dataReal, CM, CMi, VHT=dataProcessing.getRealData("Data/DatenSerra_Cleaned.xlsx")
    meanReal=dataReal[CM].mean(axis=1)
    print(meanReal.to_list())
    '''
    meanReal=np.array([0.0, 0.10803020724516467, 0.26178633324363587, 0.4924801776220496, 0.6810856362149192, 0.8889627225596783, 1.0792922770303692, 1.2977144942365675, 1.5171184397268414, 1.7315336251261078, 1.9325481716952009, 2.182095975741178, 2.4450662434032666, 2.6799076028615354, 2.9498880169326442, 3.188864796784648, 3.427356169045465, 3.6593222627091126, 3.9162297221312463, 4.193548310465519, 4.415471355607272, 4.638137885239214, 4.858648053661321, 5.084631308316655, 5.310581638122003, 5.553929688124145, 5.766957292475154, 5.97817980884844, 6.226785520559159, 6.460218753516072, 6.67717817660153, 6.86186219872761, 7.083982181150214, 7.295366033459195, 7.509615428915179, 7.701338534422805, 7.890576325661254, 8.087535839649307, 8.27071637456442, 8.495251826481361, 8.686382745779406, 8.885300270419494, 9.04465400650687, 9.22622349780609, 9.387570568933025, 9.5463838650117, 9.692870531723912, 9.808247012027453, 9.996295848067764, 10.170467050368705, 10.308934524471976, 10.444840517830633, 10.594440893675602, 10.751299586033129, 10.906533589685983, 11.031598079119707, 11.17353522497797, 11.30536401491214, 11.42440618772565, 11.550745636215925, 11.706272507656385, 11.805386912048458, 11.940750464900756, 12.078632696504378, 12.216084732987797, 12.328515017701436, 12.412066659122303, 12.537865870595493, 12.660645381781688, 12.799788038788057, 12.880116927258072, 13.019832848429992, 13.122728976473102, 13.25206605719081, 13.423424446385116, 13.534995248092654, 13.639312887436358, 13.761387832425084, 13.840303322101015, 13.948891884741895, 14.04973785129704, 14.166579106713648, 14.245149139977787, 14.35708172946961, 14.467311734692089, 14.558888370734268, 14.682211298834083, 14.767506804686978, 14.882754921636195, 14.982636653981057, 15.064985697793068, 15.169595211220782, 15.25998370572961, 15.337929809237963, 15.416244305597758, 15.497587659951819, 15.593984370472738, 15.675647929409662, 15.747533341000038, 15.821924419017392, 15.920727690022021, 15.990996913815955, 16.055019815430068, 16.122476862368075, 16.203145459453314, 16.31596367970407, 16.378453770960558, 16.45890305106895, 16.54369308025633, 16.60965377513323, 16.683109256169427, 16.746750677764243, 16.826838100821696, 16.904215374453283, 16.98445282481348, 17.040009862923238, 17.108762343128674, 17.191196267904196, 17.278066455014805, 17.363917733196505, 17.404542376594076, 17.460858482067287, 17.536832014117493, 17.60488143945238, 17.691418142212825, 17.750525160904353, 17.804604731530386, 17.86590498736803, 17.930561798646977, 18.006978797709113, 18.083837486794906, 18.152682944372206, 18.2212050257461, 18.295519993303387, 18.363723725316056, 18.40878890651265, 18.463741500403557, 18.545727366754303, 18.615152736059475, 18.687236171946395, 18.748760145930945, 18.77619138314718, 18.836480955465873, 18.89216977506098, 18.926985469926603, 18.994801271126, 19.078281466045162, 19.147959665196336, 19.201628933142988, 19.249747717949152, 19.311536589316205, 19.410671925521815, 19.45869990492302, 19.494981054958103, 19.56419508003736, 19.60944436155436, 19.652027512026137, 19.693988272513415, 19.769854889748473, 19.81912161939319, 19.86853334135196, 19.927553228078025, 19.998638304065995, 20.04780429660818, 20.098756976858194, 20.14945675363586, 20.189192206365213, 20.245968764861527, 20.28638921551787, 20.336546630469098, 20.38018222086935, 20.440334306221082, 20.50711479473618, 20.557976654655192, 20.610442308446924, 20.66445212374524, 20.70145866838536, 20.73989123975765, 20.76116566978642, 20.82871377371455, 20.867609912981518, 20.910653501732835, 20.990328146392006, 21.055321376677963, 21.106021725426174, 21.12912542006405, 21.164080247300156, 21.208954879269967, 21.254460447812107, 21.302555867585326, 21.357298252087197, 21.402289643871878, 21.468107386750503, 21.48835189663916, 21.54124250292704, 21.58927824479368, 21.64249859205605, 21.674071924017017, 21.732756589179402, 21.773096573887894, 21.818211666575227, 21.86893328646794, 21.898914514604527, 21.957028907897254, 21.989854153055294, 22.036816891987506, 22.08940853992911, 22.139182586886996, 22.17397050146166, 22.22366592844267, 22.260599568324803, 22.282206767119643, 22.327870613766326, 22.372978888828982, 22.41941029058393, 22.467482446782295, 22.494375686494156, 22.526310617423913, 22.582768511422778, 22.64421691155602, 22.67123338655503, 22.71269769598093, 22.768803969183473, 22.826047464463297, 22.886426206139486, 22.903744106580522, 22.92895701038894, 22.961185250118984, 22.996331817879906, 23.03552711624603, 23.06592354959403, 23.09806220410219, 23.155768841430724, 23.152428388861356, 23.22480653287364, 23.240771747345843, 23.279897558917714, 23.316925868271582, 23.383095104671956, 23.41959524949416, 23.454657328027512, 23.506217112193056, 23.55655994212204, 23.597385081598294, 23.62862942026668, 23.667557114363515, 23.694187750311148, 23.708805590257963, 23.762550876782118, 23.797264074612634, 23.8257106162239, 23.84627585511184, 23.88760181716477, 23.948034515827583, 23.97742954061369, 24.017688947862506, 24.06262700555236, 24.104581084455194, 24.128867028979407, 24.17500500985969, 24.20541494446126, 24.239408748674048, 24.271672285267954, 24.28506844566023, 24.320490942055326, 24.33575108328637, 24.36941541035906, 24.43170676091138, 24.4380101883004, 24.485230206100915, 24.521610801571285, 24.547657763823945, 24.57398096718256, 24.606320421174203, 24.63052852311957, 24.67223057574073, 24.70547886499206, 24.71666669530751, 24.77568728643558, 24.832292232975238, 24.862026983310418, 24.858733527905564, 24.895198113740165, 24.92825066006888, 24.96704116653262, 25.01573332868758, 25.021940627801616, 25.05862898795401, 25.09422106469615, 25.134815984080838, 25.137527697601108, 25.209593263639132, 25.234780669410778, 25.25042397490203, 25.300005761346846, 25.326945180510535, 25.35539693515023, 25.39730303901434, 25.421820057542572, 25.44319172908763, 25.476584621996302, 25.527753717788134, 25.548828147288763, 25.578325897431824, 25.627940422282435, 25.617595363311068, 25.650295929781414, 25.703756686474375, 25.720769976378502, 25.752390501513393, 25.808449781850424, 25.82082327666214, 25.855983732917284, 25.85471387267843, 25.88427244465615, 25.94501314643871, 26.000071352532288, 26.02530557590384, 26.02752495190342, 26.067788111869497, 26.11989239637457, 26.12772505780403, 26.14916449443561, 26.210937894510185, 26.251167346450103, 26.27847707800811, 26.3149470604295, 26.311524214334586, 26.376562891854338, 26.416658850209146, 26.442077181921615, 26.46806875448315, 26.528113243220513, 26.549537269905734, 26.553485465229045, 26.59865415749975, 26.596520814300995, 26.615071366660704, 26.635219526413426, 26.668606624342292, 26.691662209270724, 26.68978353592928, 26.749288972741528, 26.774087585166594, 26.802756075366204, 26.856710405279845, 26.870022201931704, 26.828093813297926, 26.83930031690914, 26.837506350734504, 26.85079611937476, 26.82399390660627, 26.8050492929721, 26.762565724670313, 26.756129566440297, 26.72588390424794, 26.648971860750112, 26.611265127455237, 26.575326061881622, 26.434437330867816, 24.026457923231565, 21.826628817775433, 19.872002571566313, 18.148271661357477, 16.769981420769483, 15.479367752668818, 14.287166738426516, 13.202290492812505, 12.185878435804998, 11.340751012031392])
    
    #check if dataframe exists
    if relLatency is not None:
        #mean squared error
        new=(relLatency-meanReal)**2
        #score=new.mean()
        score=new.sum()/(meanReal**2).sum()#NMSE: normalize by 2Hz's own sum-of-squares ("energy") so both protocols compete on equal footing
        myPrint("Score ADS: "+str(score),nr, name)
        return score

    return float('inf')

def eval2HzCMi(args):
    a, b, c, q, name, nr, prot=args
    params=[a, b, c, q]
        
    data_stim=stimulationProtocols.setStimulationProtocol(15)
    
    relLatency=convolution.clacLatency(data_stim, params)
    '''
    dataReal, CM, CMi, VHT=dataProcessing.getRealData("Data/DatenSerra_Cleaned.xlsx")
    meanReal=dataReal[CMi].mean(axis=1)
    print(meanReal.to_list())
    '''
    meanReal=np.array([0.0, -0.452351856241701, -0.5029901366804727, -0.2630007179215074, 0.058648245558257095, 0.45514191294670464, 0.8334852212495603, 1.1818421100730632, 1.5184270909878843, 1.850351634768251, 2.17494690993023, 2.5706451193700777, 2.964702508953265, 3.3275306997459215, 3.6598243034647373, 3.9867640976919327, 4.307140484392352, 4.615581184583073, 4.901540519271876, 5.154878096399635, 5.5256935027200305, 5.8482353207337905, 6.129351261663627, 6.400494389825396, 6.6641313997763145, 6.956657336089258, 7.234149164537619, 7.504701068283153, 7.772087490940381, 8.058304415132508, 8.314792204948349, 8.583096938528772, 8.860211482369662, 9.101911098800732, 9.330818395914097, 9.655363063078326, 9.893020182578804, 10.107459352894839, 10.338073887907072, 10.553205322725828, 10.76495127752175, 10.936562182975914, 11.12083095274175, 11.326064922986898, 11.613455498155648, 11.779649265355845, 11.986106108821708, 12.352463678899266, 12.536620448114666, 12.732654279036467, 12.917786560764723, 13.101897551963598, 13.128660383606274, 13.366192483354794, 13.572974089151355, 13.745731131132878, 13.91841133767782, 14.11350868169856, 14.270673099389912, 14.428587404014687, 14.594281042453394, 14.764220756262324, 14.89760682531511, 15.057201006203641, 15.206495819075444, 15.369806388530469, 15.512850160604915, 15.638347695140954, 15.823359224431579, 15.971574436315597, 16.13615378063169, 16.271543623330352, 16.40524222858946, 16.53689815954157, 16.70940820692471, 16.84530357652544, 16.963620074555905, 17.083550099654616, 17.228451756873937, 17.35148706275079, 17.46587450342046, 17.575432447500624, 17.74960450329306, 17.874937344898335, 18.000690520844245, 18.092174118732462, 18.236623193263167, 18.368060083036596, 18.51014844696244, 18.63518815119904, 18.74948262234504, 18.857711868014913, 18.978243366187563, 19.08932581169606, 19.19731763317868, 19.324023212152163, 19.436940655698162, 19.567299130764756, 19.754707407242755, 19.79990007045986, 19.966732644999485, 20.05744034267825, 20.172858868027493, 20.298097285151453, 20.403931862681898, 20.504102426731492, 20.51185643132413, 20.661829702574884, 20.756635579818624, 20.882688050634027, 20.98702507494755, 21.063718768065996, 21.177678841426907, 21.313770960540758, 21.393787282070377, 21.510672879779857, 21.62582788862832, 21.743490018277516, 21.832601611082982, 21.93599414949296, 22.029126375010353, 22.1160398141994, 22.198626883827917, 22.322599561447475, 22.59010823746743, 22.491174311593237, 22.777149288057178, 22.67693949064153, 22.75822851764494, 22.843512326255123, 23.155161570480672, 23.066344534638755, 23.14684300319956, 23.204312990812433, 23.269782999667036, 23.550315877151405, 23.438205201875643, 23.713166099008323, 23.61410611306033, 23.910294804266567, 23.847486693881716, 24.06621539873046, 24.16048736518504, 24.23473417712287, 24.313860544015135, 24.229134167522744, 24.466937971252538, 24.523490238611284, 24.59588361725512, 24.671730074299916, 24.75464935287132, 24.8506312285835, 24.777265565082622, 25.038294464166484, 25.11231301631775, 25.188661342748087, 25.259208672377515, 25.189845451732047, 25.432267512286614, 25.528410245263927, 25.59095393688011, 25.673401659294687, 25.766938721037302, 25.70691003173256, 25.830015767689474, 26.04098394089321, 26.09318240914885, 26.0465477010126, 26.336808428099875, 26.395352045614118, 26.45463367608263, 26.402194212749546, 26.480659643487996, 26.654650512862332, 26.709038292226346, 26.792516287687388, 26.829924318136595, 26.782928495584162, 26.926177458580863, 26.97401001293184, 27.05650477078175, 27.12794246047121, 27.2163078964513, 27.31366591355814, 27.379183395965423, 27.453642523156706, 27.534082054532718, 27.604647231894052, 27.66179136726255, 27.75154688076762, 27.816845732550046, 27.88608471303204, 27.951160385186682, 28.041791598013454, 28.114738354571355, 28.202733042963967, 28.21695430584304, 28.33253425427432, 28.399373103847807, 28.458570178006283, 28.524868913303056, 28.56212205736354, 28.63690602359554, 28.69959337162835, 28.760904939527876, 28.86594569827315, 28.942342944629672, 29.01448271070719, 29.09308380440947, 29.138232076555553, 29.197439129793473, 29.255060069974295, 29.322639243008382, 29.377225121977663, 29.46631250912253, 29.535443849691983, 29.580730397316895, 29.64539001039086, 29.69121917092064, 29.76140535622534, 29.806248048008193, 29.883969977447443, 29.91907475643717, 30.005216512423537, 30.097594282672816, 30.15436999586981, 30.206180480085415, 30.27837346654067, 30.33448251497282, 30.404869243835105, 30.476532508311198, 30.551194829753566, 30.62049459850113, 30.669937822545094, 30.68153886186886, 30.762550420837744, 30.834745407829207, 30.907377524129235, 30.98588975728933, 31.039436772001885, 31.094015805816653, 31.119728690161924, 31.190153813117664, 31.269797751142256, 31.34094706323773, 31.398695572455814, 31.41577942644486, 31.483136809181058, 31.538283133020673, 31.600556945469233, 31.651544004748576, 31.680825950199853, 31.78170636034224, 31.810263718406926, 31.87664000362808, 31.92295728784822, 31.967099017892142, 32.06188846504931, 32.13159029895537, 32.22953011394258, 32.25062733977325, 32.28787519165289, 32.36423563288049, 32.41641919805986, 32.47715525353783, 32.53904797090787, 32.58545711917039, 32.65548615370652, 32.713292163989095, 32.72716930199027, 32.77669448846932, 32.8196203550523, 32.85876991713855, 32.93657360000677, 32.96859029023664, 33.0376317325536, 33.10519243830805, 33.133832033796736, 33.18203118132982, 33.24138406241269, 33.305556466791614, 33.36277362175657, 33.42390904094903, 33.48453407243895, 33.55771356402005, 33.5841327247007, 33.648864343168945, 33.72127621759998, 33.75326033822782, 33.82870844660273, 33.89347121483518, 33.93328028636315, 34.03081279312693, 34.087720835360805, 34.12181197037165, 34.19080259814974, 34.246970024128345, 34.25986976794417, 34.305098327365954, 34.345084849441776, 34.385177741500705, 34.42697625565457, 34.484160585581876, 34.56369111321009, 34.60024598659715, 34.70224240974613, 34.72232189956714, 34.769441253881254, 34.85424100329896, 34.882070655764736, 34.95321241454553, 35.026138995284754, 35.05613604577584, 35.11637958155968, 35.17882736671137, 35.232099182257066, 35.29104341093651, 35.36020768910936, 35.4153177733219, 35.45688506089247, 35.511136830270594, 35.5075011151277, 35.528331505083614, 35.59344910585804, 35.64803471447608, 35.70132141365097, 35.72162593483368, 35.76606416887449, 35.82058460676526, 35.89355853511096, 35.92830437525096, 35.96176285462549, 36.01857633372489, 36.0660401358279, 36.07717913515788, 36.1548673774445, 36.212958226246066, 36.282540661724866, 36.346679581141885, 36.420708263054294, 36.442412397957696, 36.50255320167928, 36.560759720259036, 36.60267732136902, 36.64413370539832, 36.69670275134051, 36.70376239362361, 36.74802578347436, 36.77985453883369, 36.82481985138233, 36.88015985307178, 36.91117217065104, 36.987320648561195, 37.04642284359525, 37.09322021155838, 37.14359908927025, 37.25874791433179, 37.25505012013876, 37.27491656951598, 37.18102218193905, 36.277160935353855, 35.29854216103006, 34.15390932187697, 33.28758942431153, 32.48600517487917, 31.666662265134534, 30.955952923059304, 30.155419344873227, 29.362378412883764, 28.56019869000376])
    
    #check if dataframe exists
    if relLatency is not None:
        #mean squared error
        new=(relLatency-meanReal)**2
        score=new.mean()
        myPrint("Score ADS: "+str(score),nr, name)
        return score
    
    return float('inf')

'''
def eval2HzCM(args):
    a, b, c, name, nr, prot=args
    params=[a, b, c]
        
    data_stim=stimulationProtocols.setStimulationProtocol(15)
    
    relLatency=convolution.clacLatency(data_stim, params)
    
    #check if dataframe exists
    if relLatency is not None:       
        adsReal=0.2734662513253399*100
        adsModel=relLatency[359]
        scoreAds=abs((adsModel-adsReal))
        #print(relLatency[359][1])
        
        try:
            y=relLatency[0:360]
            #print(y)
            x=range(len(y))
            params=scipy.optimize.curve_fit(func,  x,  y)
            curvatureModel=params[0][0]#curvature 2Hz
            curvatureReal=0.008902892431610545
            scoreCurvature=abs((curvatureModel-curvatureReal))
            #print(curvature)
        except:
            myPrint("eval2HzCM: Can not calculate curvature for particle "+str(nr),nr, name)
            scoreCurvature=float('inf')
            
        #recovery after 8 pulses!
        adsRecoveryModel=relLatency[367]
        adsRecoveryReal=0.13852683146864914*100
        scoreRecovery=abs((adsRecoveryModel-adsRecoveryReal))
        #print(relLatency[367][1])
        
        try:
            y=relLatency[360:368]
            #print(y)
            x=range(len(y))
            params=scipy.optimize.curve_fit(funcRec,  x,  y)
            curvatureRecoveryModel=params[0][0]#curvature recovery
            curvatureRecoveryReal=0.14000838619822673
            scoreCurvatureRecovery=abs((curvatureRecoveryModel-curvatureRecoveryReal))
            #print(curvatureRecoveryModel)
        except:
            myPrint("eval2HzCM: Can not calculate curvature for particle "+str(nr),nr, name)
            scoreCurvatureRecovery=float('inf')
            
        
        scoreADSTotal=(scoreAds+scoreRecovery)/2
        myPrint("eval2HzCM: score ADS "+str(scoreADSTotal)+" for particle "+str(nr),nr, name)
        scoreCurvatureTotal=(scoreCurvature+scoreCurvatureRecovery)/2
        myPrint("eval2HzCM: score curvature "+str(scoreCurvatureTotal)+" for particle "+str(nr),nr, name)
        score=(scoreADSTotal+scoreCurvatureTotal)/2
        return score
        
    return float('inf')
 
def eval2HzCMi(args):
    a, b, c, name, nr, prot=args
    params=[a, b, c]
    
    data_stim=stimulationProtocols.setStimulationProtocol(15)
        
    relLatency=convolution.clacLatency(data_stim, params)
    
    #check if dataframe exists
    if relLatency is not None:
        adsReal=0.37458764208290524*100
        adsModel=relLatency[359]
        scoreAds=abs((adsModel-adsReal))
        
        try:
            y=relLatency[0:360]
            #print(y)
            x=range(len(y))
            params=scipy.optimize.curve_fit(func,  x,  y)
            curvatureModel=params[0][0]#curvature 2Hz
            curvatureReal=0.006883246072126799
            scoreCurvature=abs((curvatureModel-curvatureReal))
            #print(curvature)
        except:
            myPrint("eval2HzCMi: Can not calculate curvature for particle "+str(nr),nr, name)
            scoreCurvature=float('inf')
            
        #recovery after 8 pulses!
        adsRecoveryModel=relLatency[367]
        adsRecoveryReal=0.302302279609007*100
        scoreRecovery=abs((adsRecoveryModel-adsRecoveryReal))
        #print(relLatency[367][1])
        
        try:
            y=relLatency[360:368]
            #print(y)
            x=range(len(y))
            params=scipy.optimize.curve_fit(funcRec,  x,  y)
            curvatureRecoveryModel=params[0][0]#curvature recovery
            curvatureRecoveryReal=0.08195372433529731
            scoreCurvatureRecovery=abs((curvatureRecoveryModel-curvatureRecoveryReal))
            #print(curvatureRecoveryModel)
        except:
            myPrint("eval2HzCMi: Can not calculate curvature for particle "+str(nr),nr, name)
            scoreCurvatureRecovery=float('inf')
            
        
        scoreADSTotal=(scoreAds+scoreRecovery)/2
        myPrint("eval2HzCMi: score ADS "+str(scoreADSTotal)+" for particle "+str(nr),nr, name)
        scoreCurvatureTotal=(scoreCurvature+scoreCurvatureRecovery)/2
        myPrint("eval2HzCMi: score curvature "+str(scoreCurvatureTotal)+" for particle "+str(nr),nr, name)
        score=(scoreADSTotal+scoreCurvatureTotal)/2
        return score
    return float('inf')
'''
def evalRecoveryCycleCM(args):
    d, e1, e2, f2, g, h, q, name, nr, prot=args
    params=[d, e1, e2, f2, g, h, q]

    #HARD CONSTRAINT: reject any particle whose simulated 0.5Hz response drops more than 1%
    #below zero at the reference ISIs - the real digitized CM fiber data (0.5Hz reference curve)
    #never goes negative (min +0.5346%). Folded directly into this protocol (rather than a
    #separate weighted one) so all optimization pressure stays on fitting CM's own real
    #recovery-cycle data; the reference curve only narrows which solutions are eligible.
    #Denser re-digitization (36 points, ~9-313ms) - the original 12-point set had a gap between
    #210ms and 290ms that let a -0.43% dip at ISI=250ms slip through uncaught (opt-Nonlinear-
    #Convo-CM5-constrained); this set brackets that gap with points at 245ms and 255ms.
    ref_05hz_isi_ms=[8.835388494661041, 9.638588917739954, 12.851451890319957, 13.654652313398985, 22.489979527795732, 26.50604292345465, 34.5381697147726, 41.76709608301146, 48.99602245125038, 57.028149242568276, 65.86347645696507, 75.50200409444085, 83.53413088575869, 92.36945810015555, 102.81124744097441, 112.44977507845019, 122.08836399619021, 130.92369121058707, 139.75901842498382, 149.39760734272383, 158.23293455712056, 167.06826177151743, 176.70678940899333, 186.34537832673323, 194.37750511805106, 203.2128323324479, 213.65462167326683, 224.09634973382154, 234.53813907464055, 244.97986713519515, 255.4216564760142, 262.650582844253, 272.28911048172887, 282.7308998225477, 293.1726278831025, 303.6144172239213, 313.25294486139705]
    #0.5Hz reference slowing (%) at ref_05hz_isi_ms, same order - recovered from the 2026-09-11 digitization
    #(8.835ms was digitized twice, 6.069 and 5.786 - their average 5.928 is used)
    ref_05hz_slowing=[5.927673518047058, 5.471698724319619, 5.0314472613891805, 4.716981845039556, 4.371069767095933,
                      4.339623105501934, 4.245282520924755, 4.088049812749942, 3.8993716425714937, 3.7106922728026834,
                      3.522012903033872, 3.3333341330602426, 3.144653563701066, 2.9559753935226194, 2.767296023753808,
                      2.5786172537801786, 2.4213845456053664, 2.2012573146521923, 2.075472467661742, 1.9496864210809297,
                      1.8553464362989316, 1.761007051312117, 1.6352210047313036, 1.5723264819529421, 1.477988296556491,
                      1.2893089267876805, 1.2264156035996814, 1.1006289572236878, 1.0377368336260535, 0.9433962490488753,
                      0.7861635408740616, 0.754717479075245, 0.6918241558872481, 0.6603780940884293, 0.6289308326992491,
                      0.5974847709004324, 0.5345914477124356]
    extras_05hz = sorted(set(x/1000 for x in ref_05hz_isi_ms), reverse=True)

    #def customDPProtocol(freq, extras):
    def customDPProtocol(freq, extras, numberPrevPulses=100):
        vec=[]
        #numberPrevPulses=100
        for i in range(1,numberPrevPulses+1):
            vec.append(i*freq)
        lastPulse=numberPrevPulses*freq
        numReg=30
        for e in extras:
            vec.append(lastPulse+freq-e)
            for i in range(1,numReg+1):
                vec.append(lastPulse+i*freq)
            lastPulse=lastPulse+numReg*freq
        return vec

    #CM15 (opt-Nonlinear-Convo-CM15-fb-2hz-only, 2026-10-12): score = 2Hz reference fit ONLY.
    #The 0.25Hz fit (CM's own data), the 0.5Hz negativity penalty and the 0.5Hz value fit are no longer
    #scored. The 2Hz score is computed first and returned here; the old combined-score code below
    #is kept but unreachable. REVERT: delete this block to get back the CM12-CM14 combined score.
   
    extras_2hz = [0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.015, 0.010, 0.005]#s (250..5.4ms)
    ref_2hz_slowing_new = [-0.0126186483981679, -1.14042063939205, -2.56735868835626, -5.32109723687196,
                           -6.07211958160769, -7.04844445562701, -7.84953209662154, -8.25007649686006,
                           -7.5761585810345515, 0.06457042273689659]
    prevPulses_2hz = 800#same starting-pulse count as DP2hz / run_plot.py's prevPulses[0.5]
    stim_2hz = stimulationProtocols.setStimulationProtocol("DP2hz")#2Hz background, 800 starting pulses, extras 250..5ms
    lat_2hz = convolution.convolution_vec(stim_2hz, lambda x, y: convolution.memory_2D(x, y, params))
    if lat_2hz is None:#same "simulation failed" check the 0.25Hz branch used to do
        return float('inf')
    sim_2hz = [lat_2hz[i+2]-lat_2hz[i] for i in range(prevPulses_2hz-1, len(lat_2hz)-2, 31)]
    score_2hz = np.mean([abs(s-r) for s, r in zip(sim_2hz, ref_2hz_slowing_new)])
    #return score_2hz#CM15: mean absolute error to the 10-point 2Hz reference (%)

    #Latest run (opt-Nonlinear-Convo-CM15-fb-2hz-025-newbounds, 2026-10-13): add CM's own 0.25Hz recovery cycle
    #back with a SMALL weight. The 2Hz-only best (CM15-fb-2hz-newbounds, 2Hz MAE 0.057) had 0.25Hz MAE 3.35 (curve
    #negative) because 2Hz alone barely constrains q. Separate differential-evolution trade-off test (current bounds): w=0.3 -> 2Hz 0.055 / 0.25Hz 0.128;
    #w=1 -> 0.065/0.117; w=10 -> 0.42/0.063. Same 0.25Hz MAE as the old score_025 below (DP protocol,
    #100 starting pulses, 11 extras). REVERT: comment out from here to the return and restore "return score_2hz"
    data_stim_025 = stimulationProtocols.setStimulationProtocol("DP")#0.25Hz background, 100 starting pulses, 11 extras
    lat_025 = convolution.convolution_vec(data_stim_025, lambda x, y: convolution.memory_2D(x, y, params))
    if lat_025 is None:
        return float('inf')
    realValues_025 = [0.240241491, 0.252928694, 0.296115416, 0.546602641, 1.450783851, 2.515537532, 3.780695111, 4.167464007, 4.516383778, 4.916885365, 5.386598886]
    sim_025 = [lat_025[i+2]-lat_025[i] for i in range(99, len(lat_025)-2, 31)]#same readout as the old code (100 prev pulses, 30 regular)
    score_025 = np.mean([abs(s-r) for s, r in zip(sim_025[:11], realValues_025)])
    w_025 = 0.3#small weight - keeps the 2Hz fit (~0.055) while bringing the 0.25Hz MAE from ~3.35 to ~0.13
    return score_2hz + w_025*score_025

    #--- everything below is the CM12-CM14 combined score, unreachable since CM15 (kept for REVERT) ---
    #data_stim=stimulationProtocols.setStimulationProtocol("DP2hz")
    data_stim=stimulationProtocols.setStimulationProtocol("DP")#0.25Hz background - fit to CM's own measured 0.25Hz data (DP2hz is now the 2Hz protocol, used below)

    l=convolution.convolution_vec(data_stim, lambda x, y: convolution.memory_2D(x, y, params))
    #print(l)

    #check if dataframe exists
    if l is not None:
        #extras=[2000, 1000, 500, 250, 150, 100, 50, 40, 30, 20, 15]#distance to next regular puls

        realValues=[0.240241491, 0.252928694, 0.296115416, 0.546602641, 1.450783851, 2.515537532, 3.780695111, 4.167464007, 4.516383778, 4.916885365, 5.386598886]

        #matches _Final_2D_RecoveryCycle2-vectorized.ipynb's getRecoveryCycle(): shift = latency of the
        #regular pulse right after the extra minus latency of the regular pulse right before it,
        #skipping the extra pulse's own latency entirely
        numberPrevPulses=100
        numberRegPulses=30
        recoveryCycle=[l[i+2]-l[i] for i in range(numberPrevPulses-1, len(l)-2, numberRegPulses+1)]

        numberOfExtra=11#total number of extra pulses
        score=0

        for i in range(numberOfExtra):
            score=score+abs(recoveryCycle[i]-realValues[i])

        #return score/numberOfExtra
        score_025 = score/numberOfExtra#fit to CM's own 0.25Hz recovery cycle (unchanged)

        #SOFT 2Hz SCORE (no hard constraint - every particle gets a finite score): mean absolute
        #distance to the new digitized 2Hz reference curve, read at the supervisor-specified ISIs
        #(the DP-protocol extras that fit inside a 0.5s period). Rewards the dip, trading a little
        #0.25Hz fit quality for it (separate differential-evolution test: 0.25Hz MAE 0.071 -> 0.079, 2Hz MAE ~6.5 -> 0.15)
        #extras_2hz = [0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.015]#s (250..15ms)
        #ref_2hz_slowing_new = [-0.0126186483981679, -1.14042063939205, -2.56735868835626, -5.32109723687196,
        #                       -6.07211958160769, -7.04844445562701, -7.84953209662154, -8.25007649686006]
        #+2 points (10.46ms, 5.36ms): covers the curve's rise back toward 0 at very short ISIs
        extras_2hz = [0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.015, 0.010, 0.005]#s (250..5.4ms)
        ref_2hz_slowing_new = [-0.0126186483981679, -1.14042063939205, -2.56735868835626, -5.32109723687196,
                               -6.07211958160769, -7.04844445562701, -7.84953209662154, -8.25007649686006,
                               -7.5761585810345515, 0.06457042273689659]
        #stim_2hz = customDPProtocol(0.5, extras_2hz)#period=0.5s -> 2Hz
        #sim_2hz = [lat_2hz[i+2]-lat_2hz[i] for i in range(99, len(lat_2hz)-2, 31)]
        prevPulses_2hz = 800#same starting-pulse count as run_plot.py's prevPulses[0.5], so score and plot match
        #stim_2hz = customDPProtocol(0.5, extras_2hz, prevPulses_2hz)#period=0.5s -> 2Hz
        stim_2hz = stimulationProtocols.setStimulationProtocol("DP2hz")#2Hz background, 800 starting pulses, same extras as extras_2hz
        lat_2hz = convolution.convolution_vec(stim_2hz, lambda x, y: convolution.memory_2D(x, y, params))
        sim_2hz = [lat_2hz[i+2]-lat_2hz[i] for i in range(prevPulses_2hz-1, len(lat_2hz)-2, 31)]
        score_2hz = np.mean([abs(s-r) for s, r in zip(sim_2hz, ref_2hz_slowing_new)])

        #SOFT 0.5Hz PENALTY (replaces the old hard gate - no particle ever gets inf): the real 0.5Hz
        #reference never goes negative, so penalize only how far the simulated curve dips below 0,
        #averaged over the 37 reference ISIs. A curve that stays >= 0 adds nothing.
        stim_05hz = customDPProtocol(2, extras_05hz)#period=2s -> 0.5Hz, 100 starting pulses as before
        lat_05hz = convolution.convolution_vec(stim_05hz, lambda x, y: convolution.memory_2D(x, y, params))
        sim_05hz = [lat_05hz[i+2]-lat_05hz[i] for i in range(99, len(lat_05hz)-2, 31)]
        score_05hz = np.mean([max(0.0, -s) for s in sim_05hz])
        #SOFT 0.5Hz FIT: mean absolute distance to the 37-point 0.5Hz reference values (sim_05hz is in
        #extras_05hz order = descending ISI, the reference is ascending -> match by ISI)
        sim_05hz_map = dict(zip(extras_05hz, sim_05hz))
        score_05hz_fit = np.mean([abs(sim_05hz_map[x/1000]-y) for x, y in zip(ref_05hz_isi_ms, ref_05hz_slowing)])

        w_2hz = 0.1#weight of the 2Hz term relative to the 0.25Hz fit
        w_05hz = 0.1#weight of the 0.5Hz negativity penalty relative to the 0.25Hz fit
        w_05hz_fit = 0.1#weight of the 0.5Hz value fit - same as the 2Hz term (same units, similar range)
        #return score_025 + w_2hz*score_2hz
        #return score_025 + w_2hz*score_2hz + w_05hz*score_05hz
        return score_025 + w_2hz*score_2hz + w_05hz*score_05hz + w_05hz_fit*score_05hz_fit
    return float('inf')

def evalRecoveryCycleCMi(args):
    d, e, f, name, nr, prot=args
    params=[d, e, f]
    '''
    #20 pulses at 0.25 Hz -> one pulse every 4 seconds
    #to stabilize latency
    vec=[]
    offset=0
    for i in range(1,21):
        vec.append(offset+i*4)
    lastPulse=offset+20*4
    extras=[2, 1, 0.5, 0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.015]#distance to next regular puls
    numReg=5#number of regular pulses
    for e in extras:
        #one extra pulse
        vec.append(lastPulse+4-e)
        #regular pulses
        for i in range(1,numReg+1):
            vec.append(lastPulse+i*4)
        lastPulse=lastPulse+numReg*4
    '''
    data_stim=stimulationProtocols.setStimulationProtocol("DP")
    
    l=convolution.clacLatency_2(data_stim, params)
    
    #check if dataframe exists
    if l is not None:
        #extras=[2000, 1000, 500, 250, 150, 100, 50, 40, 30, 20, 15]#distance to next regular puls
        realValues=[0.324487317, 0.249044214, -0.176721166, 0.452664143, 1.463325936, 1.798056359, 3.110076518, 2.838785715, 3.442295076, 3.763976836, 3.681834103]

        numberOfExtra=11#total number of extra pulses
        numRegPulses=6#number of regular pulses in between extra pulses
        score=0

        for i in range(numberOfExtra):
            l1=l[19+i*numRegPulses]#latency of regular pulse
            l2=l[21+i*numRegPulses]#latency of next regular pulse
            if l1!=-1 and l2!=-1:
                shift=l2-l1
                score=score+abs(shift-realValues[i])
 
        return score/numberOfExtra
    return float('inf')

#calculates score for specific following frequency for CMi 
def ffCMi(args, freq):
    d, e, f, name, nr, prot=args
    params=[d, e, f]

    prot="FF_"+str(freq)+"Hz_ADS"
    stim=stimulationProtocols.setStimulationProtocol(prot)
    #print(stim)
    
    l=convolution.clacLatency_2(stim, params)
    #print(l)

    #check if dataframe exists
    if l is not None: 
        #Vivien: CMi, 2-4-8
        if freq==10:
            realFF=[0.92, 2.26, 4.52]
        elif freq==20:
            realFF=[1.42,3.07,5.48]
        elif freq==50:
            realFF=[1.27,2.47,4.57]
        elif freq==100:
            realFF=[0.84, 0.91,0.99]

        ff=[l[22]-l[19], l[36]-l[31], l[54]-l[45]]
        
        return (abs(ff[0]-realFF[0])+abs(ff[1]-realFF[1])+abs(ff[2]-realFF[2]))/3
    return float('inf')

#calculates score for specific following frequency for CM
def ffCM(args, freq):
    d, e, f, name, nr, prot=args
    params=[d, e, f]
    
    prot="FF_"+str(freq)+"Hz_ADS"
    stim=stimulationProtocols.setStimulationProtocol(prot)
    #print(stim)
    
    l=convolution.clacLatency_2(stim, params)
    #print(l)
    
    #check if dataframe exists
    if l is not None:  
        #Vivien: CM, 2-4-8
        if freq==10:
            realFF=[0.92, 2.26, 4.52]
        elif freq==20:
            realFF=[0.32, 0.81, 2.61]
        elif freq==50:
            realFF=[0.32, 0.92, 2.44]
        elif freq==100:
            realFF=[0.27, 0.27, 0.32]

        ff=[l[22]-l[19], l[36]-l[31], l[54]-l[45]]
        
        return (abs(ff[0]-realFF[0])+abs(ff[1]-realFF[1])+abs(ff[2]-realFF[2]))/3
    return float('inf')

