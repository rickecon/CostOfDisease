# Simulating the costs of disease

The scripts in this directory are set up to simulate the cost of disease for South Africa.  This is determined in `main.py` which calibrates OG-Core to South African data and then simulates the cost of disease for South Africa.

Descriptions of files in this directory:
* `main.py`: This is the script to execute. It runs the simulations and saves the results to disk.
* `get_pop_data.py`: This script has utilities to get the population data for the baseline and to compute the counterfactual population under increased mortality.
* `create_plots_tables.py`: This script has utilities to create plots and tables for the results.