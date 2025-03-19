# This script creates the plots and tables used in the paper on the
# costs of excess deaths due to the lack of foreign aid.

# ipmort the necessary libraries
import matplotlib.pyplot as plt
import numpy as np
import os
from ogcore import parameter_plots as pp
from ogcore.utils import pct_change_unstationarized

# Use a custom matplotlib style file for plots
plt.style.use("ogcore.OGcorePlots")


def plots(base_tpi, base_params, reform_dict, forecast, plot_path):
    """
    Create plots and tables for the cost of disease

    Args:
        base_tpi (dict): baseline TPI output
        base_params (Specifications): baseline parameters
        reform_dict (dict): dictionary of reform results
        forecast (pd.DataFrame): forecast of macro variables
        plot_path (str): path to save plots

    """

    # Set constants
    BASELINE_YEAR_TO_PLOT = 2035
    TIME_SERIES_PLOT_END_YEAR = 2100
    NUM_YEARS_NPV = 100
    YEAR_RANGE_MIN = 2040
    YEAR_RANGE_MAX = YEAR_RANGE_MIN + 9

    # Plot mortality rates in the baseline and reform(s)
    tpi_list = [base_tpi] + [
        reform_dict[k]["tpi_vars"] for k in reform_dict.keys()
    ]
    labels_list = ["Baseline"] + [k for k in reform_dict.keys()]
    fig = pp.plot_mort_rates(
        tpi_list,
        labels=labels_list,
        years=[BASELINE_YEAR_TO_PLOT],
        include_title=False,
        path=plot_path,
    )

    # Create table of level changes in macro variables
    # Read in CBO long-term forecast  # TODO: find some forecast of South
    # African GDP over a long time period (or extrapolate from some shorter term forecast)
    forecast = XXXX
    # compute percentage changes in macro variables
    GDP_series = {
        "Baseline": forecast,
        "Pct changes": {},
        "Levels": {},
        "Diffs": {},
    }
    for k in reform_dict.keys():
        GDP_series["Pct Changes"][k] = pct_change_unstationarized(
            base_tpi,
            base_params,
            reform_dict[k]["tpi_vars"],
            reform_dict[k]["params"],
            output_vars=["Y"],
        )
        GDP_series["Levels"][k] = GDP_series["Baseline Forecast"] * (
            1 + GDP_series["Pct Changes"][k]
        )
        GDP_series["Diffs"][k] = (
            GDP_series["Levels"][k] - GDP_series["Baseline Forecast"]
        )

    # Find avg change in GDP from begin_window to end_window
    results_first_N_years = {}
    for k in reform_dict.keys():
        results_first_N_years[k] = (
            GDP_series["Diffs"][k]
            .loc[
                (
                    GDP_series["Diffs"][k].index
                    >= (YEAR_RANGE_MIN - reform_dict[k]["params"].start_year)
                )
                & (
                    GDP_series["Diffs"][k].index
                    <= (YEAR_RANGE_MAX - reform_dict[k]["params"].start_year)
                )
            ]
            .mean()
        )
    # TODO: save this table to disk

    # Find NPV of levels of GDP over NUM_YEARS_NPV years
    results_NPV = {}
    npv_dict = {
        "Discount Rate": [0.02, 0.04, 0.06],
        "Discount Rate Label": [r"2\%", r"4\%", r"6\%"],
    }
    for k in reform_dict.keys():
        results_NPV[k] = {}
        for r in npv_dict["Discount Rate"]:
            results_NPV[k][r] = (
                (
                    GDP_series["Diffs"][k].loc[
                        (GDP_series["Diffs"][k][:NUM_YEARS_NPV])
                    ]
                )
                * (1 + r) ** np.arange(NUM_YEARS_NPV)
            ).sum()
    # TODO: save this table to disk: rows are different r, columns are different reform scenarios
    # # Save table to disk
    # formatted_table = pd.DataFrame(npv_dict)
    # formatted_table.reset_index().to_latex(
    #     buf=os.path.join(plot_path, "Baseline_npv_gdp_table.tex"),
    #     index=False,
    #     index_names=False,
    #     float_format="%.2f",
    # )

    # Time series plots
    # log GDP
    fig, ax = plt.subplots()
    idx = TIME_SERIES_PLOT_END_YEAR - base_params.start_year
    years = np.arange(base_params.start_year, TIME_SERIES_PLOT_END_YEAR)
    plt.plot(
        years,
        np.log(GDP_series["Baseline"][:idx]),
        label="Baseline",
    )
    for k in reform_dict.keys():
        plt.plot(
            years,
            np.log(GDP_series[k]["Levels"][:idx]),
            label=k,
        )
    plt.legend()
    plt.xlabel("Year")
    plt.ylabel("GDP, ln(Trillions of Rand)")
    plt.savefig(os.path.join(plot_path, "log_GDP_paths.png"), dpi=300)

    # Differences in GDP
    fig, ax = plt.subplots()
    idx = TIME_SERIES_PLOT_END_YEAR - base_params.start_year
    years = np.arange(base_params.start_year, TIME_SERIES_PLOT_END_YEAR)
    for k in reform_dict.keys():
        plt.plot(
            years,
            GDP_series[k]["Diffs"][:idx],
            label=k,
        )
    plt.legend()
    plt.xlabel("Year")
    plt.ylabel("Change in GDP (Trillions of Rand)")
    plt.savefig(os.path.join(plot_path, "GDP_diff_path.png"), dpi=300)
