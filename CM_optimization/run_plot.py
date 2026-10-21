import glob
import os

import plot
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
import pandas as pd
import convolution
import stimulationProtocols



#finds the most recently modified linear-part optimization run and returns its best position,
#reading the same way plot.plotParticles2D() does (same file, same parsePosition helper)
def get_latest_linear_params(pattern="Results/opt-Linear-*"):
    candidates = [d for d in glob.glob(pattern) if os.path.isdir(d)]
    if not candidates:
        raise FileNotFoundError(f"No results folders matching {pattern}")

    latest_dir = max(candidates, key=os.path.getmtime)
    name = os.path.basename(latest_dir)

    filename = 'Results/'+str(name)+'/'+str(name)+'_bestParticles.csv'
    dataBest = pd.read_csv(filename)
    dataBest['Position'] = dataBest['Position'].apply(plot.parsePosition)#make string to list

    dbLength = len(dataBest)
    params = dataBest["Position"][dbLength-1]#last row = final best, since rows are only appended on improvement
    score = dataBest["Score"][dbLength-1]

    print(f"Loaded best params from {filename}: {params} (score={score})")
    return params


#plots each linear-part run's final best score against how many iterations it ran for
def plot_score_vs_iterations(pattern="Results/opt-Linear-*-run*"):
    dirs = sorted([d for d in glob.glob(pattern) if os.path.isdir(d)], key=os.path.getmtime)

    iterations = []
    scores = []
    labels = []
    for d in dirs:
        name = os.path.basename(d)
        bestFile = os.path.join(d, f"{name}_bestParticles.csv")
        particleFile = os.path.join(d, f"{name}particle0.csv")

        dataBest = pd.read_csv(bestFile)
        totalIterations = len(pd.read_csv(particleFile))#one row per iteration, per particle

        iterations.append(totalIterations)
        scores.append(dataBest["Score"].iloc[-1])#last row = final best
        labels.append(name.replace('opt-Linear-Convo-CM-',''))

    plt.figure()
    plt.plot(iterations, scores, marker='o', color="red")
    for x, y, label in zip(iterations, scores, labels):
        plt.annotate(label, (x, y), textcoords="offset points", xytext=(5,5), fontsize=8)
    plt.xlabel('number of iterations')
    plt.ylabel('best score')
    plt.title('Best score vs. iterations run')


#finds the most recently modified nonlinear-part optimization run and returns its best (7-param) position,
#same pattern as get_latest_linear_params()
def get_latest_nonlinear_params(pattern="Results/opt-Nonlinear-Convo-CM*"):
    candidates = [d for d in glob.glob(pattern) if os.path.isdir(d)]
    if not candidates:
        raise FileNotFoundError(f"No results folders matching {pattern}")

    #walk newest-to-oldest and skip any run whose bestParticles.csv has 0 rows (every particle
    #scored inf, e.g. a failed hard-constraint run like opt-Nonlinear-Convo-CM8-fb-2hz) - picking
    #that as "latest" used to crash on dataBest["Position"][-1] (KeyError: -1, empty frame)
    for latest_dir in sorted(candidates, key=os.path.getmtime, reverse=True):
        name = os.path.basename(latest_dir)
        filename = 'Results/'+str(name)+'/'+str(name)+'_bestParticles.csv'
        dataBest = pd.read_csv(filename)

        if len(dataBest) == 0:
            print(f"Skipping {filename}: no valid (non-inf) particles recorded")
            continue

        dataBest['Position'] = dataBest['Position'].apply(plot.parsePosition)#make string to list

        dbLength = len(dataBest)
        params = dataBest["Position"][dbLength-1]#last row = final best, since rows are only appended on improvement
        score = dataBest["Score"][dbLength-1]

        print(f"Loaded best nonlinear params from {filename}: {params} (score={score})")
        return params

    raise FileNotFoundError(f"No folder matching {pattern} has any valid (non-inf) particles")


#"DP" recovery-cycle protocol, parameterized by background frequency (1/freq Hz) instead of the fixed 1/4Hz,
#matching _Final_2D_RecoveryCycle2-vectorized.ipynb's protDP(freq)
def setDPProtocol(freq, numberPrevPulses=100):
    vec=[]
    for i in range(1,numberPrevPulses+1):
        vec.append(i*freq)
    lastPulse=numberPrevPulses*freq
    extras=[2, 1, 0.5, 0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.015, 0.010, 0.005]#distance to next regular pulse
    #drop extras >= the background period itself - those would land at or before the previous
    #regular pulse (non-monotonic/zero ISI), which breaks for short periods like 2Hz (period=0.5s)
    extras=[e for e in extras if e<freq]
    numReg=30#number of regular pulses
    for e in extras:
        vec.append(lastPulse+freq-e)
        for i in range(1,numReg+1):
            vec.append(lastPulse+i*freq)
        lastPulse=lastPulse+numReg*freq
    return vec


#extracts latency-shift-vs-ISI from a recovery-cycle simulation,
#matching _Final_2D_RecoveryCycle2-vectorized.ipynb's getRecoveryCycle()
def getRecoveryCycle(l, numberPrevPulses=100):
    numberRegPulses=30
    return [l[i+2]-l[i] for i in range(numberPrevPulses-1, len(l)-2, numberRegPulses+1)]


#tells whether the most recently modified optimization run is a linear-part or nonlinear-part run,
#by comparing the newest folder matching each naming pattern - whichever stage you last ran wins
def get_latest_stage():
    linear_dirs = [d for d in glob.glob("Results/opt-Linear-*") if os.path.isdir(d)]
    nonlinear_dirs = [d for d in glob.glob("Results/opt-Nonlinear-Convo-CM*") if os.path.isdir(d)]

    latest_linear = max((os.path.getmtime(d) for d in linear_dirs), default=-1)
    latest_nonlinear = max((os.path.getmtime(d) for d in nonlinear_dirs), default=-1)

    if latest_linear==-1 and latest_nonlinear==-1:
        raise FileNotFoundError("No linear or nonlinear results folders found")

    return "nonlinear" if latest_nonlinear > latest_linear else "linear"


force_stage = "nonlinear"  # set to "linear" or "nonlinear" to override auto-detection

stage = force_stage if force_stage else get_latest_stage()
print(f"Latest stage: {stage}")

# ---------------- Combined memory function surface (linear + nonlinear, one function) ----------------
#memory_2D already stitches both regimes together via np.where: the frozen run15+fb a,b,c linear
#branch for ISI>=0.5s, and the fitted d,e1,e2,f2,g,h,q nonlinear branch for ISI<0.5s - this is
#the exact function the nonlinear stage was fit against, so it's plotted here regardless of
#`stage`, rather than only when stage=="nonlinear"
nonlinear_params = get_latest_nonlinear_params()

isi_range = np.arange(0, 0.6, 0.005)#interstimulus interval (s)
pa_range = np.arange(0, 20, 0.1)#pre-existing slowing (%)
ISI, PA = np.meshgrid(isi_range, pa_range)
M = convolution.memory_2D(ISI, PA, nonlinear_params)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(PA, ISI, M, rstride=1, cstride=1, cmap=cm.RdBu, linewidth=0, antialiased=False, vmin=-5, vmax=10)
ax.zaxis.set_major_locator(LinearLocator(10))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
ax.set_xlabel('pre-existing slowing (%)')
ax.set_ylabel('interstimulus interval (s)')
ax.set_zlabel('latency shift (%)')
ax.set_title('Memory function (linear + nonlinear combined)')
fig.colorbar(surf, shrink=0.5, aspect=5)

if stage=="linear":
    params = get_latest_linear_params()
    plot_score_vs_iterations()

    # ---------------- Linear memory function surface ----------------
    #ISI vs. PA, matching the style of the nonlinear
    #memory function surface plot below - vmin/vmax omitted since the linear part's range is
    #much smaller than the nonlinear part's.
    isi_range = np.arange(0, 350, 1)#interstimulus interval (s) - extended to cover the full ELID/2Hz protocol duration, not just the 0-0.6s transition zone
    pa_range = np.arange(0, 30, 0.5)#pre-existing slowing (%) - extended to match the real latency range seen in the 2Hz protocol (up to ~26-37%)
    ISI, PA = np.meshgrid(isi_range, pa_range)
    M_linear = convolution.memory_feedback(ISI, PA, params)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(PA, ISI, M_linear, rstride=1, cstride=1, cmap=cm.RdBu, linewidth=0, antialiased=False)
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
    ax.set_xlabel('pre-existing slowing (%)')
    ax.set_ylabel('interstimulus interval (s)')
    ax.set_zlabel('latency shift (%)')
    ax.set_title('Linear memory function')
    fig.colorbar(surf, shrink=0.5, aspect=5)

    # ---------------- ELID protocol ----------------
    data_stim_elid = stimulationProtocols.setStimulationProtocol(11)
    relLatency_elid = convolution.convolution_vec(data_stim_elid, lambda x, y: convolution.memory_feedback(x, y, params))

    realLatency_elid = pd.read_csv("ELID_CM.csv", index_col=0)["0"].values[:len(data_stim_elid)]

    #per-fiber mean+SD from the raw Excel data, for error bars on the same plot - SD (not SEM)
    #per supervisor request, to show actual fiber-to-fiber spread rather than precision of the mean
    dataReal_elid, CM_elid, CMi_elid, VHT_elid = plot.dataProcessing.getRealData("Data/DatenELID_Cleaned.xlsx")
    mean_elid = dataReal_elid[CM_elid].mean(axis=1)
    std_elid = dataReal_elid[CM_elid].std(axis=1)

    plt.figure()
    plt.scatter(data_stim_elid, relLatency_elid, color="red", label="simulated")
    plt.scatter(data_stim_elid, realLatency_elid, color="black", label="real data")
    plt.errorbar(data_stim_elid, mean_elid[0:len(data_stim_elid)], std_elid[0:len(data_stim_elid)], linestyle='None', marker='.', label="CM (per-fiber)", color="grey", ecolor="lightgrey")
    plt.xlabel('time (s)')
    plt.ylabel('latency (%)')
    plt.title('ELID protocol')
    plt.legend()

    # ---------------- 2Hz protocol ----------------
    data_stim_2hz = stimulationProtocols.setStimulationProtocol(15)
    relLatency_2hz = convolution.convolution_vec(data_stim_2hz, lambda x, y: convolution.memory_feedback(x, y, params))

    realLatency_2hz = pd.read_csv("Serra_CM.csv", index_col=0)["0"].values

    #per-fiber mean+SD from the raw Excel data, for error bars on the same plot - SD (not SEM)
    #per supervisor request, to show actual fiber-to-fiber spread rather than precision of the mean
    dataReal_2hz, CM_2hz, CMi_2hz, VHT_2hz = plot.dataProcessing.getRealData("Data/DatenSerra_Cleaned.xlsx")
    mean_2hz = dataReal_2hz[CM_2hz].mean(axis=1)
    std_2hz = dataReal_2hz[CM_2hz].std(axis=1)

    plt.figure()
    plt.scatter(data_stim_2hz, relLatency_2hz, color="red", label="simulated")
    plt.scatter(data_stim_2hz, realLatency_2hz, color="black", label="real data")
    plt.errorbar(data_stim_2hz, mean_2hz[0:len(data_stim_2hz)], std_2hz[0:len(data_stim_2hz)], linestyle='None', marker='.', label="CM (per-fiber)", color="grey", ecolor="lightgrey")
    plt.xlabel('time (s)')
    plt.ylabel('latency (%)')
    plt.title('2Hz protocol')
    plt.legend()

elif stage=="nonlinear":
    # ---------------- Recovery cycle protocol ----------------
    #nonlinear_params already loaded above (used by the combined memory function surface)
    extras=[2, 1, 0.5, 0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.015, 0.010, 0.005]
    realValues_rc=[0.240241491, 0.252928694, 0.296115416, 0.546602641, 1.450783851, 2.515537532, 3.780695111, 4.167464007, 4.516383778, 4.916885365, 5.386598886]

    data_stim_rc = stimulationProtocols.setStimulationProtocol("DP")
    relLatency_rc = convolution.convolution_vec(data_stim_rc, lambda x, y: convolution.memory_2D(x, y, nonlinear_params))

    #raw simulated latency over the whole protocol, matching the notebook's first "Recovery Cycle" plot
    plt.figure()
    plt.plot(data_stim_rc, relLatency_rc, marker='.', linestyle='none')
    plt.xlabel('time (s)')
    plt.ylabel('latency (%)')
    plt.title('Recovery Cycle')

    plt.figure()
    #extras now has 13 entries (down to 5ms) but the 0.25Hz data/"DP" protocol has 11 -> use the first 11
    plt.plot(extras[:11][::-1], realValues_rc[::-1], linestyle='-', marker='.', label="CM (real)", color="black")
    plt.scatter(extras[:11][::-1], getRecoveryCycle(relLatency_rc)[::-1], label="simulated", color="red")
    plt.xlabel('interstimulus interval (s)')
    plt.ylabel('latency shift (%)')
    plt.title('Recovery cycle')
    plt.legend()

    # ---------------- Recovery cycle at 2Hz background (DP2hz protocol) ----------------
    #same protocol, starting pulses and reference as the 2Hz term in evaluateMPI.evalRecoveryCycleCM
    extras_2hz=[0.25, 0.15, 0.1, 0.05, 0.04, 0.03, 0.02, 0.015, 0.010, 0.005]
    ref_2hz=[-0.0126186483981679, -1.14042063939205, -2.56735868835626, -5.32109723687196,
             -6.07211958160769, -7.04844445562701, -7.84953209662154, -8.25007649686006,
             -7.5761585810345515, 0.06457042273689659]
    data_stim_2hz_dp = stimulationProtocols.setStimulationProtocol("DP2hz")
    relLatency_2hz_dp = convolution.convolution_vec(data_stim_2hz_dp, lambda x, y: convolution.memory_2D(x, y, nonlinear_params))

    plt.figure()
    plt.plot(extras_2hz[::-1], ref_2hz[::-1], linestyle='-', marker='.', label="reference, 2 Hz", color="black")
    plt.scatter(extras_2hz[::-1], getRecoveryCycle(relLatency_2hz_dp, 800)[::-1], label="simulated, 2 Hz", color="red")
    plt.xlabel('interstimulus interval (s)')
    plt.ylabel('latency shift (%)')
    plt.title('Recovery cycle - 2 Hz background (DP2hz)')
    plt.legend()

    # ---------------- Recovery cycle: background frequency sensitivity ----------------
    freqs = {20: "1/20 Hz", 12: "1/12 Hz", 8: "1/8 Hz", 4: "1/4 Hz", 2: "1/2 Hz", 1: "1 Hz", 0.5: "2 Hz"}
    #2Hz (period 0.5s) is still climbing after 100 starting pulses, so it gets more starting
    #pulses to settle before the extra pulses begin; all other frequencies keep the default 100
    #1Hz also hasn't settled after 100 starting pulses (latency change over the last 10: +0.21%);
    #300 brings that down to ~0.001%
    prevPulses = {1: 300, 0.5: 800}

    freq_stims = {}
    freq_lats = {}
    for freq, label in freqs.items():
        freq_stims[freq] = setDPProtocol(freq, prevPulses.get(freq, 100))
        freq_lats[freq] = convolution.convolution_vec(freq_stims[freq], lambda x, y: convolution.memory_2D(x, y, nonlinear_params))

    #raw simulated latency over time, one trace per background frequency, matching the notebook's style
    plt.figure()
    for freq, label in freqs.items():
        plt.plot(freq_stims[freq], freq_lats[freq], marker='.', linestyle='none', label=f"simulated, {label}")
    plt.xlabel('time (s)')
    plt.ylabel('latency (%)')
    plt.title('Recovery Cycle - background frequency sensitivity')
    plt.legend(loc="upper right")

    plt.figure()
    plt.plot(extras[:11][::-1], realValues_rc[::-1], linestyle='-', marker='.', label="CM (real), 1/4 Hz", color="black")
    for freq, label in freqs.items():
        #each frequency's own extras (setDPProtocol drops extras>=freq internally, so periods
        #shorter than some extras - like 2Hz's 0.5s period - produce a shorter list than the
        #shared `extras`)
        freq_extras = [e for e in extras if e<freq]
        plt.plot(freq_extras[::-1], getRecoveryCycle(freq_lats[freq], prevPulses.get(freq, 100))[::-1], marker='.', label=f"simulated, {label}")

    plt.xlabel('interstimulus interval (s)')
    plt.ylabel('latency shift (%)')
    plt.title('Recovery cycle - background frequency sensitivity')
    plt.legend()

plt.show()
