# Modelling-of-Memory-in-Unmyelinated-Axons
An efficient model to predict conduction velocity changes in unmyelinated axons, based on "memory" where prior activity modulates subsequent action potential speeds. Incorporating linear long-term and non-linear short-term memory components, it predicts propagation speeds using a memory function.

## Requirements:
- Python

## Installation and Usage:
- download the files
- examples how to use the 1D and 2D model are given in the corresponding Notebook files
- convolution_1D.py and convolution_2D.py contain the respective definitions of the memory functions and the function that convolves the memory function with a given signal/stimulation protocol
- stimulationProtocols.py defines examplary signals for the convolution
- plot.py contains some functions to plot the resulting latencies of the pre-defined stimulation protocols

## Citation:
(for details see the CITATION.cff) If you refer to this project in an article, we would appreciate it if you cited the preprint:

If you actively used the library to gain results in your publication, it might also make sense for you to cite the specific release via the Zenodo archive. On the right side, you will see an individual DOI listed for each version released since v1.0.0. Just pick the DOI matching your version. Alternatively, you can also cite all versions of this library.
