#!/usr/bin/zsh

### Job name
#SBATCH --job-name=NeuronGEPSO

### File for the output
#SBATCH --output=NeuronGEPSO_OUTPUT

### Time your job needs to execute, e. g. 50 min
#SBATCH --time=5:00:00

### Memory your job needs per node, e. g. 250 MB
#SBATCH --mem=3900M

### Use more than one node for parallel jobs on distributed-memory systems, e. g. 2
#SBATCH --nodes=1

### Number of CPUS per task (for distributed-memory parallelisation, use 1)
#SBATCH --cpus-per-task=3

### Disable hyperthreading by setting the tasks per core to 1
#SBATCH --ntasks-per-core=1

### Number of processes per node, e. g. 6 (6 processes on 2 nodes = 12 processes in total)
#SBATCH --ntasks-per-node=1

###send mail if status of program changes
#SBATCH --mail-type=ALL

#SBATCH --mail-user=anna.maxion@rwth-aachen.de

### Change to working directory
cd /home/am373735/"Neuron Model"

### Run your parallel application
module load Python/3.10.4

python run.py