# This script will run the simulations of OG-ZAF to account for
# more excess deaths do to the lack of foreign aid.

# imports
import multiprocessing
from distributed import Client
import os
import json
import time
import copy
import numpy as np
import pandas as pd
from importlib.resources import files
import matplotlib.pyplot as plt
from ogcore.parameters import Specifications
from ogcore.execute import runner
from ogcore.utils import safe_read_pickle
import ogzaf
import get_pop_data
import create_plots_tables

# set country to South Africa
UN_COUNTRY_CODE = "710"


def main():
    # Define parameters to use for multiprocessing
    num_workers = min(multiprocessing.cpu_count(), 7)
    client = Client(n_workers=num_workers, threads_per_worker=1)
    print("Number of workers = ", num_workers)

    # Directories to save data
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))
    save_dir = os.path.join(CUR_DIR, "CostOutput")
    base_dir = os.path.join(save_dir, "BASELINE")
    median_dir = os.path.join(save_dir, "MedianDeaths")
    low_dir = os.path.join(save_dir, "LowDeaths")
    high_dir = os.path.join(save_dir, "HighDeaths")
    plot_path = os.path.join(save_dir, "Plots")
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)

    """
    ---------------------------------------------------------------------------
    Run baseline policy
    ---------------------------------------------------------------------------
    """
    # Set up baseline parameterization
    p = Specifications(
        baseline=True,
        num_workers=num_workers,
        baseline_dir=base_dir,
        output_base=base_dir,
    )
    # Update parameters for baseline from default json file
    with files("ogzaf").joinpath("ogzaf_default_parameters.json").open(
        "r"
    ) as file:
        defaults = json.load(file)
    p.update_specifications(defaults)

    # get baseline population data (rather than use what is in JSON)
    pop_dict, fert_rates, mort_rates, infmort_rates, imm_rates = (
        get_pop_data.baseline_pop(p)
    )
    p.update_specifications(pop_dict)

    # Run model
    start_time = time.time()
    # runner(p, time_path=True, client=client)
    print("run time = ", time.time() - start_time)

    """
    ---------------------------------------------------------------------------
    Simulate with baseline ("median") excess deaths
    ---------------------------------------------------------------------------
    """

    # create new Specifications object for reform simulation
    p2 = copy.deepcopy(p)
    p2.baseline = False
    p2.output_base = median_dir

    # Find new population with excess deaths
    new_pop_dict = get_pop_data.disease_pop(
        p2,
        fert_rates,
        mort_rates,
        infmort_rates,
        imm_rates,
        UN_COUNTRY_CODE,
        # excess_deaths=202_693,
        # excess_deaths=228_881,  # Annals of Internal Medicine Base Case, complete cutback (PEPFAR = 0%) = 2_186_000 over 10 years + CGD estimates for the other diseases
        # 10,481
        excess_deaths=301_581,  # Annals of Internal Medicine Susceptible scenario, complete cutback (PEPFAR = 0%) = 2_911_000 over 10 years + CGD estimates for the other diseases
        # 10,481
    )
    p2.update_specifications(new_pop_dict)

    # Apply productivity losses for the hiv and tb effects
    # These are not time or income group specific. One time permanent effect
    # Define the adjustment factors
    hiv_adjustment = 0.00190705  # HIV-driven adjustment (as a percentage)
    tb_adjustment = 0.00027581  # Tuberculosis adjustment (as a percentage)

    # Compute the total adjustment factor (percentage increase)
    total_adjustment = hiv_adjustment + tb_adjustment  # ≈ 0.00218286

    # Update the disutility of labor matrix for the entire population
    p2.chi_n = p2.chi_n * (1 + total_adjustment)

    # Run model
    start_time = time.time()
    # runner(p2, time_path=True, client=client)
    print("run time = ", time.time() - start_time)

    """
    ---------------------------------------------------------------------------
    Simulate "low" scenario, with 50% of the median excess deaths (and 50% of productivity losses)
    ---------------------------------------------------------------------------
    """
    # create new Specifications object for reform simulation
    p3 = copy.deepcopy(p)
    p3.baseline = False
    p3.output_base = low_dir

    # Find new population with excess deaths
    new_pop_dict = get_pop_data.disease_pop(
        p3,
        fert_rates,
        mort_rates,
        infmort_rates,
        imm_rates,
        UN_COUNTRY_CODE,
        excess_deaths=202_693 * 0.5,
    )
    p3.update_specifications(new_pop_dict)

    # Apply productivity losses for the bottom 70% of the population
    # these are a linear interpolation of the four scenario values
    prod_low = {}
    for year, value in productivity_adjustments.items():
        prod_low[year] = value * 0.5

    # Iterate over each simulation year assuming simulation starts at 2025
    for t in range(p3.e.shape[0]):
        current_year = p3.start_year + t  # e.g. 2025, 2026, ...
        adjustment = get_adjustment(prod_low, current_year)
        p3.e[t, :, :3] = p.e[t, :, :3] * (1 + adjustment)

    # Run model
    start_time = time.time()
    # runner(p3, time_path=True, client=client)
    print("run time = ", time.time() - start_time)

    """
    ---------------------------------------------------------------------------
    Simulate "high" scenario, with 150% of the median excess deaths (and 150% of productivity losses)
    ---------------------------------------------------------------------------
    """
    # create new Specifications object for reform simulation
    p4 = copy.deepcopy(p)
    p4.baseline = False
    p4.output_base = high_dir

    # Find new population with excess deaths
    new_pop_dict = get_pop_data.disease_pop(
        p4,
        fert_rates,
        mort_rates,
        infmort_rates,
        imm_rates,
        UN_COUNTRY_CODE,
        excess_deaths=202_693 * 1.5,
    )
    p4.update_specifications(new_pop_dict)

    # Apply productivity losses for the bottom 70% of the population
    # these are a linear interpolation of the four scenario values
    prod_high = {}
    for year, value in productivity_adjustments.items():
        prod_high[year] = value * 1.5

    # Iterate over each simulation year assuming simulation starts at 2025
    for t in range(p4.e.shape[0]):
        current_year = p4.start_year + t  # e.g. 2025, 2026, ...
        adjustment = get_adjustment(prod_low, current_year)
        p4.e[t, :, :3] = p.e[t, :, :3] * (1 + adjustment)

    # Run model
    start_time = time.time()
    # runner(p4, time_path=True, client=client)
    print("run time = ", time.time() - start_time)
    client.close()

    """
    ---------------------------------------------------------------------------
    Create output
    ---------------------------------------------------------------------------
    """
    base_tpi = safe_read_pickle(os.path.join(base_dir, "TPI", "TPI_vars.pkl"))
    base_params = safe_read_pickle(os.path.join(base_dir, "model_params.pkl"))

    # put reform(s) in dict
    # If do other sims (e.g, with high and low forecasts of excess deaths), they
    # can be added to this dictionary
    reform_dict = {
        "Low Excess Deaths": {
            "tpi_vars": safe_read_pickle(
                os.path.join(low_dir, "TPI", "TPI_vars.pkl")
            ),
            "params": safe_read_pickle(
                os.path.join(low_dir, "model_params.pkl")
            ),
        },
        "Median Excess Deaths": {
            "tpi_vars": safe_read_pickle(
                os.path.join(median_dir, "TPI", "TPI_vars.pkl")
            ),
            "params": safe_read_pickle(
                os.path.join(median_dir, "model_params.pkl")
            ),
        },
        "High Excess Deaths": {
            "tpi_vars": safe_read_pickle(
                os.path.join(high_dir, "TPI", "TPI_vars.pkl")
            ),
            "params": safe_read_pickle(
                os.path.join(high_dir, "model_params.pkl")
            ),
        },
    }

    # Create tables and plots
    # read in real GDP forecast
    forecast_df = pd.read_csv(os.path.join(CUR_DIR, "real_gdp_forecast.csv"))
    forecast = forecast_df[forecast_df.year >= base_params.start_year][
        "real_gdp"
    ].values
    create_plots_tables.plots(
        base_tpi, base_params, reform_dict, forecast, plot_path
    )


if __name__ == "__main__":
    # execute only if run as a script
    main()
