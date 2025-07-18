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
    medium_dir = os.path.join(save_dir, "MediumDeaths")
    low_dir = os.path.join(save_dir, "LowDeaths")
    high_dir = os.path.join(save_dir, "HighDeaths")
    # aim_dir = os.path.join(save_dir, "AIMDeaths")

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
    (
        pop_dict,
        pop_dist,
        pre_pop_dist,
        fert_rates,
        mort_rates,
        infmort_rates,
        imm_rates,
        baseline_deaths,
    ) = get_pop_data.baseline_pop(p)
    p.update_specifications(pop_dict)

    # Run model
    start_time = time.time()
    runner(p, time_path=True, client=client)
    print("run time = ", time.time() - start_time)

    """
    ---------------------------------------------------------------------------
    Simulate the scenario consistent with excess deaths from Gandhi et al.
    (2025)
    ---------------------------------------------------------------------------
    """

    # create new Specifications object for reform simulation
    p2 = copy.deepcopy(p)
    p2.baseline = False
    p2.output_base = medium_dir

    # Find new population with excess deaths
    new_pop_dict, medium_deaths = get_pop_data.disease_pop(
        p2,
        pop_dist,
        pre_pop_dist,
        fert_rates,
        mort_rates,
        infmort_rates,
        imm_rates,
        UN_COUNTRY_CODE,
        excess_deaths=132_600,
    )
    p2.update_specifications(new_pop_dict)

    # Apply productivity losses for the hiv and tb effects
    # These are not time or income group specific. One time permanent effect
    # Define the adjustment factors
    hiv_adjustment = 0.0036062  # HIV-driven adjustment (as a percentage)
    tb_adjustment = 0.00027581  # Tuberculosis adjustment (as a percentage)

    total_adjustment = hiv_adjustment + tb_adjustment  # ≈ 0.003882

    # Update the disutility of labor matrix for the entire population
    p2.chi_n = p2.chi_n * (1 + total_adjustment)

    # Run model
    start_time = time.time()
    runner(p2, time_path=True, client=client)
    print("run time = ", time.time() - start_time)

    """
    ---------------------------------------------------------------------------
    Simulate the scenario consistent with excess deaths from Brink, et al.
    (2025)
    ---------------------------------------------------------------------------
    """
    # create new Specifications object for reform simulation
    p3 = copy.deepcopy(p)
    p3.baseline = False
    p3.output_base = low_dir

    # Find new population with excess deaths
    new_pop_dict, low_deaths = get_pop_data.disease_pop(
        p3,
        pop_dist,
        pre_pop_dist,
        fert_rates,
        mort_rates,
        infmort_rates,
        imm_rates,
        UN_COUNTRY_CODE,
        excess_deaths=98_350,
    )
    p3.update_specifications(new_pop_dict)

    # Low productivity adjustment scenario
    low_prod = total_adjustment * 0.5

    # Update the disutility of labor matrix for the entire population
    p3.chi_n = p3.chi_n * (1 + low_prod)

    # Run model
    start_time = time.time()
    runner(p3, time_path=True, client=client)
    print("run time = ", time.time() - start_time)

    """
    ---------------------------------------------------------------------------
    Simulate the scenario consistent with excess deaths from Kenny and Sandefur
    (2025)
    ---------------------------------------------------------------------------
    """
    # create new Specifications object for reform simulation
    p4 = copy.deepcopy(p)
    p4.baseline = False
    p4.output_base = high_dir

    # Find new population with excess deaths
    new_pop_dict, high_deaths = get_pop_data.disease_pop(
        p4,
        pop_dist,
        pre_pop_dist,
        fert_rates,
        mort_rates,
        infmort_rates,
        imm_rates,
        UN_COUNTRY_CODE,
        excess_deaths=192_212,
    )
    p4.update_specifications(new_pop_dict)

    # High productivity adjustment scenario
    high_prod = total_adjustment * 1.5

    # Update the disutility of labor matrix for the entire population
    p4.chi_n = p4.chi_n * (1 + high_prod)

    # Run model
    start_time = time.time()
    runner(p4, time_path=True, client=client)
    print("run time = ", time.time() - start_time)

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
        "Brink, et al. (2025)": {
            "tpi_vars": safe_read_pickle(
                os.path.join(low_dir, "TPI", "TPI_vars.pkl")
            ),
            "params": safe_read_pickle(
                os.path.join(low_dir, "model_params.pkl")
            ),
            "deaths": low_deaths,
        },
        "Gandhi, et al. (2025)": {
            "tpi_vars": safe_read_pickle(
                os.path.join(medium_dir, "TPI", "TPI_vars.pkl")
            ),
            "params": safe_read_pickle(
                os.path.join(medium_dir, "model_params.pkl")
            ),
            "deaths": medium_deaths,
        },
        "Kenny and Sandefur (2025)": {
            "tpi_vars": safe_read_pickle(
                os.path.join(high_dir, "TPI", "TPI_vars.pkl")
            ),
            "params": safe_read_pickle(
                os.path.join(high_dir, "model_params.pkl")
            ),
            "deaths": high_deaths,
        },
    }

    # Create tables and plots
    # read in real GDP forecast
    forecast_df = pd.read_csv(os.path.join(CUR_DIR, "real_gdp_forecast.csv"))
    forecast = forecast_df[forecast_df.year >= base_params.start_year][
        "real_gdp"
    ].values
    create_plots_tables.plots(
        base_tpi,
        base_params,
        baseline_deaths,
        reform_dict,
        forecast,
        plot_path,
    )


if __name__ == "__main__":
    # execute only if run as a script
    main()
