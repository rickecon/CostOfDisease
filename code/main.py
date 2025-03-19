# This script will run the simulations of OG-ZAF to account for
# more excess deaths do to the lack of foreign aid.

# imports
import multiprocessing
from distributed import Client
import os
import json
import time
import copy
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
    save_dir = os.path.join(CUR_DIR, "OG-ZAF-Example")
    base_dir = os.path.join(save_dir, "OUTPUT_BASELINE")
    reform_dir = os.path.join(save_dir, "OUTPUT_REFORM")
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
    with (
        files("ogzaf")
        .joinpath("ogzaf_default_parameters.json")
        .open("r") as file
    ):
        defaults = json.load(file)
    p.update_specifications(defaults)

    # get baseline population data (rather than use what is in JSON)
    pop_dict, fert_rates, mort_rates, infmort_rates, imm_rates = (
        get_pop_data.baseline_pop(p)
    )
    p.update_specifications(pop_dict)

    # Run model
    start_time = time.time()
    runner(p, time_path=True, client=client)
    print("run time = ", time.time() - start_time)

    """
    ---------------------------------------------------------------------------
    Run reform policy
    ---------------------------------------------------------------------------
    """

    # create new Specifications object for reform simulation
    p2 = copy.deepcopy(p, UN_COUNTRY_CODE)
    p2.baseline = False
    p2.output_base = reform_dir

    # Find new population with excess deaths
    new_pop_dict = get_pop_data.disease_pop(
        p2,
        fert_rates,
        mort_rates,
        infmort_rates,
        imm_rates,
        UN_COUNTRY_CODE,
        excess_deaths=202_693,
    )
    p2.update_specifications(new_pop_dict)

    # Run model
    start_time = time.time()
    runner(p2, time_path=True, client=client)
    print("run time = ", time.time() - start_time)
    client.close()

    """
    ---------------------------------------------------------------------------
    Create output
    ---------------------------------------------------------------------------
    """
    base_tpi = safe_read_pickle(os.path.join(base_dir, "TPI", "TPI_vars.pkl"))
    base_params = safe_read_pickle(os.path.join(base_dir, "model_params.pkl"))
    reform_tpi = safe_read_pickle(
        os.path.join(reform_dir, "TPI", "TPI_vars.pkl")
    )
    reform_params = safe_read_pickle(
        os.path.join(reform_dir, "model_params.pkl")
    )
    # put reform(s) in dict
    # If do other sims (e.g, with high and low forecasts of excess deaths), they
    # can be added to this dictionary
    reform_dict = {
        "Median Excess Deaths": {
            "tpi_vars": reform_tpi,
            "params": reform_params,
        }
    }

    # Create tables and plots
    create_plots_tables.plots(
        base_tpi, base_params, reform_dict, forecast, plot_path
    )


if __name__ == "__main__":
    # execute only if run as a script
    main()
