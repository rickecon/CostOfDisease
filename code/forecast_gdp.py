import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def extend_gdp_series(
    file_path,  # Path to the CSV file containing GDP data
    long_term_growth=0.0253,  # 2.53% long-term growth rate
    convergence_years=7,  # Number of years to transition to the long-term growth rate
    forecast_years=10,  # Number of years to forecast
    plot=False,  # Whether to plot the result
    save_path=None,  # Path to save the extended series as a CSV file
):
    """
    Forecast GDP using an S-shaped growth path that transitions from the current growth rate
    to a long-term growth rate.

    Parameters:
        gdp_series (pd.Series): Historical GDP data with years as the index.
        long_term_growth (float): Target long-term growth rate (e.g., 0.0253 for 2.53%).
        convergence_years (int): Number of years to transition to the long-term growth rate.
        forecast_years (int): Number of years to forecast.
        plot (bool): Whether to plot the result.
        save_path (str): Path to save the extended series as a CSV file.

    Returns:
        pd.Series: Combined historical and forecasted GDP series.
    """
    gdp_df = pd.read_csv(file_path)
    gdp_series = pd.Series(
        data=gdp_df["real_gdp"].values, index=gdp_df["year"]
    )

    # --- Step 1: Calculate average 3-year growth rate (CAGR) ---
    gdp_t0 = gdp_series.iloc[-4]
    gdp_t3 = gdp_series.iloc[-1]
    initial_growth = (gdp_t3 / gdp_t0) ** (1 / 3) - 1

    # --- Step 2: Create S-shaped growth path ---
    x = np.linspace(
        -5, 5, convergence_years
    )  # Years before and after the transition
    logistic_curve = 1 / (1 + np.exp(-x))
    growth_rates = (
        1 - logistic_curve
    ) * initial_growth + logistic_curve * long_term_growth  #  S-shaped growth path

    # Extend flat long-term growth if needed
    if forecast_years > convergence_years:
        growth_rates = np.concatenate(
            [
                growth_rates,
                [long_term_growth] * (forecast_years - convergence_years),
            ]
        )

    # --- Step 3: Generate forecasted GDP values ---
    future_years = np.arange(
        gdp_series.index[-1] + 1, gdp_series.index[-1] + 1 + forecast_years
    )
    forecast_gdp = [gdp_series.iloc[-1]]

    for g in growth_rates:
        forecast_gdp.append(forecast_gdp[-1] * (1 + g))

    forecast_gdp = forecast_gdp[1:]

    # --- Step 4: Combine historical and forecasted series ---
    forecast_series = pd.Series(forecast_gdp, index=future_years)
    extended_series = pd.concat([gdp_series, forecast_series])

    # --- Save to CSV if save_path is provided ---
    if save_path:
        extended_series.to_csv(
            save_path, header=["real_gdp"], index_label="year"
        )

    # --- Optional Plot ---
    if plot:
        plt.figure(figsize=(10, 5))
        plt.plot(
            extended_series,
            label="Real GDP (Historical + Forecast)",
            marker="o",
        )
        plt.axvline(
            gdp_series.index[-1],
            color="gray",
            linestyle="--",
            label="Forecast Start",
        )
        plt.title("GDP Forecast with S-shaped Growth Convergence")
        plt.xlabel("Year")
        plt.ylabel("Real GDP")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    return extended_series
