These are a few samples of the possible test inputs using default parameters. Note that for impulse inputs, data collection will typically not manage to capture the spike in voltage command since it exists for only a single timestep; demo data impulse1.csv was captured by repeatedly running impulse inputs until one got lucky.

MATLAB script motorDataVisualize.m contains code to plot these data files, and an example of how to analyze a step input to determine the motor transfer function.
