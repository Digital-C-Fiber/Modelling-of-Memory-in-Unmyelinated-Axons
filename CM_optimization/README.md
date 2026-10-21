# Memory-function model of activity-dependent slowing — fit to CM fibres

This folder fits the two-dimensional memory-function model of
Maxion et al. (2026), *Modelling the memory of unmyelinated axons* (J Physiol, DOI 10.1113/JP290729),
to **mechano-responsive (CM)** human C-fibres. The original model was fitted to mechano-insensitive (CMi) fibres.

The latency of each action potential is the convolution of the fibre's spiking history with a memory function
`m(ISI, PA)` (ISI = inter-stimulus interval, PA = pre-existing slowing). The memory function has two branches:

| Branch | ISI | Form | Fitted parameters |
|---|---|---|---|
| Linear (long-term memory) | ≥ 0.5 s | `a − b·ISI + c·log1p(PA)` (floored at 0) | a, b, c |
| Nonlinear (recovery cycle) | < 0.5 s | `exp(−d·(ISI−e1)) − log(q·PA)·h·exp(−f2·(ISI−e2)) + g` | d, e1, e2, f2, g, h, q |

The parameters are fitted in two stages with a generalized particle swarm optimization (GEPSO), parallelised with MPI:
first the linear branch, then the nonlinear branch with a, b, c frozen.

## Files

| File | Purpose |
|---|---|
| `PSO_MPI_CM.py` | Main script: runs the particle swarm optimization (settings, run name) |
| `particleSwarm2GEPSO.py` | Particle update rule and parameter bounds (`lower()`, `upper()`) |
| `evaluateMPI.py` | Scores a parameter set on the stimulation protocols |
| `convolution.py` | Memory functions (`memory_feedback`, `memory_2D`) and the convolution |
| `stimulationProtocols.py` | Stimulation protocols (ELID, 2 Hz, recovery cycle "DP", "DP2hz", …) |
| `run_plot.py` | Plots the best fit of the latest linear / nonlinear run |
| `plot.py`, `dataProcessing.py` | Helper functions (reading results and data) |
| `Data/`, `ELID_CM.csv`, `Serra_CM.csv` | Microneurography data (CM fibres) – **not included**, see "Data" below |
| `Results/` | Best parameters of the final runs (see below) |
| `job.sh` | Example SLURM job script for the RWTH cluster |
| `particle.csv` | Optional starting point (only used if `positionFromParticle=True`) |
| `_Final_2D_RecoveryCycle2-vectorized.ipynb` | Reference notebook of the 2D model |

## Data

The microneurography data are not included in this repository because of ethical and privacy restrictions. Requests to access the data should be directed to Prof. B. Namer. To run the code, place `DatenELID_Cleaned.xlsx` and `DatenSerra_Cleaned.xlsx` in `Data/`, and `ELID_CM.csv` and `Serra_CM.csv` in this folder.

## Installation

```bash
pip install -r requirements.txt
```

An MPI implementation is required for the optimization: Microsoft MPI on Windows, OpenMPI or MPICH on Linux/macOS.

## Usage

**Plot the final fits** (no MPI needed):

```bash
python run_plot.py
```

Set `force_stage` in `run_plot.py` to `"linear"` or `"nonlinear"` to choose which stage is plotted.

**Run an optimization:**

1. In `PSO_MPI_CM.py`, give the run a new `name`. A safety check stops the script if `Results/<name>` already holds results.
2. Start it with `N = num_particles × num_protocols + 1` processes. For the current nonlinear settings (14 particles, 1 protocol):

```bash
mpiexec -n 15 python PSO_MPI_CM.py
```

Results are written to `Results/<name>/` (`<name>_bestParticles.csv` = global best after each improvement).
The stored score is (sum of protocol scores) / (num_protocols + 1).

**Switching to the linear stage** requires: `runEvalParticleCM_1` instead of `runEvalParticleCM_2` at the end of
`PSO_MPI_CM.py`, `dimensions=3`, `num_protocols=2`, enabling the linear `upper()` in `particleSwarm2GEPSO.py`
and removing the `d >= 200` line in `lower()`.

## Final results

| Stage | Run (folder in `Results/`) | Score | Best parameters |
|---|---|---|---|
| Linear | `opt-Linear-Convo-CM-run15+fb` | NMSE: ELID 0.0132, 2 Hz 0.0026 | a = 0.1364, b = 0.005609, c = 0.07468 |
| Nonlinear | `opt-Nonlinear-Convo-CM15-fb-2hz-025-newbounds` | MAE to the 2 Hz reference + 0.3 × MAE to the CM 0.25 Hz recovery cycle: 2 Hz 0.20 %, 0.25 Hz 0.23 % | d = 412.7, e1 = 0.01020, e2 = 0.03908, f2 = 10.43, g = 0.906, h = 2.637, q = 0.551 |

The linear parameters are frozen inside `convolution.memory_2D`.
Only the best-parameter files of these two runs are included; the full optimization histories are not.
