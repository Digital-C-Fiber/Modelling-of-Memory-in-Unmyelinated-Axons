#differential-evolution check of the nonlinear stage, used to choose the weight w in the cost function
#   S = MAE_2Hz + w * MAE_0.25Hz
#for each weight, the 7 nonlinear parameters (d, e1, e2, f2, g, h, q) are optimised with scipy's
#differential_evolution within the same bounds as the PSO (particleSwarm2GEPSO.lower/upper), and the
#two error terms of the best parameter set are reported separately
#
#run from this folder:   python de_tradeoff.py                    (weights 0.3, 1, 3, 10)
#                        python de_tradeoff.py --weights 0.3 1     (other weights)
#                        python de_tradeoff.py --quick             (short smoke test, a few generations)
#results are written to de_results/de_tradeoff_results.csv (nothing is written to Results/)
#runtime: a few minutes per weight with all CPU cores; the result varies slightly between seeds

import argparse
import csv
import os
import time

import numpy as np
from scipy.optimize import differential_evolution

import convolution
import stimulationProtocols
import particleSwarm2GEPSO as gepso

#CM recovery cycle at 0.25 Hz background (11 extra pulses, 2 s ... 15 ms), same values as evaluateMPI.evalRecoveryCycleCM
REAL_025 = [0.240241491, 0.252928694, 0.296115416, 0.546602641, 1.450783851, 2.515537532, 3.780695111,
            4.167464007, 4.516383778, 4.916885365, 5.386598886]
#2 Hz reference recovery cycle (10 points, 250 ... 5.4 ms), digitised from Bostock et al. (2003), Fig. 5A
REF_2HZ = [-0.0126186483981679, -1.14042063939205, -2.56735868835626, -5.32109723687196, -6.07211958160769,
           -7.04844445562701, -7.84953209662154, -8.25007649686006, -7.5761585810345515, 0.06457042273689659]

STIM_025 = stimulationProtocols.setStimulationProtocol("DP")      #0.25 Hz background, 100 conditioning pulses
STIM_2HZ = stimulationProtocols.setStimulationProtocol("DP2hz")   #2 Hz background, 800 conditioning pulses
PENALTY = 1e6   #cost for parameter sets that make the exponentials overflow


#latency shift of each extra pulse: regular pulse after the extra pulse minus regular pulse before it
#(30 regular pulses between extra pulses), same readout as evaluateMPI.evalRecoveryCycleCM
def recovery_cycle(latency, number_prev_pulses):
    return [latency[i+2]-latency[i] for i in range(number_prev_pulses-1, len(latency)-2, 31)]


#mean absolute errors to the 2 Hz reference and to the 0.25 Hz CM data for one parameter set
def errors(params):
    with np.errstate(all="ignore"):
        lat_2hz = convolution.convolution_vec(STIM_2HZ, lambda x, y: convolution.memory_2D(x, y, params))
        lat_025 = convolution.convolution_vec(STIM_025, lambda x, y: convolution.memory_2D(x, y, params))
    mae_2hz = np.mean(np.abs(np.subtract(recovery_cycle(lat_2hz, 800), REF_2HZ)))
    mae_025 = np.mean(np.abs(np.subtract(recovery_cycle(lat_025, 100)[:11], REAL_025)))
    return mae_2hz, mae_025


#cost S = MAE_2Hz + w * MAE_0.25Hz (defined at module level so the parallel workers can use it)
def cost(params, w):
    mae_2hz, mae_025 = errors(list(params))
    s = mae_2hz + w*mae_025
    return s if np.isfinite(s) else PENALTY


if __name__ == "__main__":   #required on Windows for the parallel workers
    parser = argparse.ArgumentParser(description="Differential-evolution trade-off test for the weight w")
    parser.add_argument("--weights", type=float, nargs="+", default=[0.3, 1, 3, 10])
    parser.add_argument("--popsize", type=int, default=15)
    parser.add_argument("--maxiter", type=int, default=150)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--quick", action="store_true", help="smoke test: 3 generations, small population")
    args = parser.parse_args()
    if args.quick:
        args.popsize, args.maxiter = 5, 3

    bounds = [(gepso.lower(i), gepso.upper(i)) for i in range(7)]   #same bounds as the PSO
    print("bounds (d, e1, e2, f2, g, h, q):", bounds)

    os.makedirs("de_results", exist_ok=True)
    out_file = os.path.join("de_results", "de_tradeoff_results.csv")
    rows = []
    for w in args.weights:
        start = time.time()
        res = differential_evolution(cost, bounds, args=(w,), popsize=args.popsize, maxiter=args.maxiter,
                                     seed=args.seed, workers=-1, updating="deferred", polish=False)
        mae_2hz, mae_025 = errors(list(res.x))
        rows.append([w, mae_2hz, mae_025, res.fun, res.nfev, round(time.time()-start, 1), *res.x])
        print(f"w = {w}: MAE 2 Hz = {mae_2hz:.4f} %, MAE 0.25 Hz = {mae_025:.4f} %, cost = {res.fun:.4f}, "
              f"evaluations = {res.nfev}, time = {time.time()-start:.0f} s")

    with open(out_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["w", "MAE_2Hz", "MAE_025Hz", "cost", "evaluations", "time_s", "d", "e1", "e2", "f2", "g", "h", "q"])
        writer.writerows(rows)
    print("saved", out_file)
