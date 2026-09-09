"""
common_data.py
==============
Synthetic data generators for microgrid optimization and forecasting examples.
Course: ELEN0445 - Microgrids, Université de Liège.

Provides realistic, physics-inspired profiles for:
- Solar photovoltaic (PV) generation (clear-sky diurnal cycle with stochastic clouds)
- Residential electric demand (baseload + morning & evening peaks)
- Time-of-Use (TOU) electricity pricing
- Representative days with seasonal weights for sizing studies
"""

import numpy as np
import pandas as pd


def generate_synthetic_pv(
    n_days: int = 1,
    resolution_min: int = 15,
    peak_kw: float = 10.0,
    cloudiness: float = 0.25,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate synthetic PV potential generation profile [kW].

    Parameters
    ----------
    n_days : int
        Number of consecutive days to simulate.
    resolution_min : int
        Time resolution in minutes (e.g., 10, 15, or 60).
    peak_kw : float
        Installed PV peak capacity [kWp].
    cloudiness : float
        Factor in [0, 1] determining the prevalence of cloud cover.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ['time_hours', 'pv_potential_kw', 'is_daylight'].
    """
    rng = np.random.default_rng(seed)
    steps_per_day = int(24 * 60 / resolution_min)
    total_steps = n_days * steps_per_day
    dt_hours = resolution_min / 60.0

    time_hours = np.arange(total_steps) * dt_hours
    hour_of_day = time_hours % 24.0

    # Solar diurnal cycle: sunrise at 06:00, sunset at 20:00 (summer-like day)
    t_rise, t_set = 6.0, 20.0
    daylight_mask = (hour_of_day >= t_rise) & (hour_of_day <= t_set)

    # Ideal clear-sky curve (half-sine)
    solar_angle = np.pi * (hour_of_day - t_rise) / (t_set - t_rise)
    sin_val = np.where(daylight_mask, np.clip(np.sin(solar_angle), 0.0, 1.0), 0.0)
    clear_sky = np.where(daylight_mask, sin_val ** 1.2, 0.0)

    # Correlated cloud cover using a filtered Gaussian random walk
    raw_cloud = rng.normal(0, 1, total_steps)
    # Moving average filter for smooth, passing clouds (correlation time ~ 1-2 hours)
    window = max(3, int(1.5 * 60 / resolution_min))
    kernel = np.ones(window) / window
    smooth_cloud = np.convolve(raw_cloud, kernel, mode="same")
    smooth_cloud = (smooth_cloud - smooth_cloud.min()) / (
        smooth_cloud.max() - smooth_cloud.min() + 1e-6
    )

    # Attenuation factor
    attenuation = 1.0 - cloudiness * smooth_cloud
    attenuation = np.clip(attenuation, 0.15, 1.0)

    pv_power = peak_kw * clear_sky * attenuation

    # Add small high-frequency sensor noise during daylight
    noise = rng.normal(0, 0.01 * peak_kw, total_steps)
    pv_power = np.where(daylight_mask, np.clip(pv_power + noise, 0, peak_kw), 0.0)

    return pd.DataFrame(
        {
            "step": np.arange(total_steps),
            "time_hours": time_hours,
            "hour_of_day": hour_of_day,
            "pv_potential_kw": pv_power,
            "is_daylight": daylight_mask,
        }
    )


def generate_synthetic_load(
    n_days: int = 1,
    resolution_min: int = 15,
    base_kw: float = 1.0,
    peak_kw: float = 6.0,
    seed: int = 101,
) -> pd.DataFrame:
    """
    Generate synthetic residential electric demand profile [kW].

    Includes baseload (refrigeration, standby), morning peak (breakfast/activity),
    mid-day base, evening peak (cooking/appliances/heating), and random variations.

    Parameters
    ----------
    n_days : int
        Number of days.
    resolution_min : int
        Time resolution in minutes.
    base_kw : float
        Continuous baseline consumption [kW].
    peak_kw : float
        Maximum peak demand [kW].
    seed : int
        Random seed.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ['time_hours', 'load_kw'].
    """
    rng = np.random.default_rng(seed)
    steps_per_day = int(24 * 60 / resolution_min)
    total_steps = n_days * steps_per_day
    dt_hours = resolution_min / 60.0

    time_hours = np.arange(total_steps) * dt_hours
    hour_of_day = time_hours % 24.0

    # Gaussian pulses for human activity peaks
    # 1. Morning peak: centered at 08:00, width ~ 1.5 h
    morning_peak = 2.0 * np.exp(-0.5 * ((hour_of_day - 8.0) / 1.2) ** 2)
    # 2. Lunch slight bump: centered at 12:30, width ~ 1.0 h
    lunch_bump = 1.0 * np.exp(-0.5 * ((hour_of_day - 12.5) / 1.0) ** 2)
    # 3. Evening peak: centered at 19:30, width ~ 2.0 h
    evening_peak = 3.5 * np.exp(-0.5 * ((hour_of_day - 19.5) / 1.8) ** 2)
    # 4. Night drop: centered around 03:00
    night_trough = -0.3 * np.exp(-0.5 * ((hour_of_day - 3.5) / 2.0) ** 2)

    deterministic_pattern = base_kw + morning_peak + lunch_bump + evening_peak + night_trough

    # Add realistic auto-correlated variations (cooking cycles, appliance bursts)
    noise = rng.normal(0, 0.35, total_steps)
    # Occasional random appliance switch-on (e.g. kettle, oven, boiler)
    spikes = rng.choice([0.0, 1.2, 2.0], size=total_steps, p=[0.90, 0.07, 0.03])

    load_kw = deterministic_pattern + noise + spikes
    # Scale to match requested bounds
    load_kw = np.clip(load_kw, 0.2 * base_kw, peak_kw)

    return pd.DataFrame(
        {
            "step": np.arange(total_steps),
            "time_hours": time_hours,
            "hour_of_day": hour_of_day,
            "load_kw": load_kw,
        }
    )


def generate_tou_tariffs(
    n_days: int = 1,
    resolution_min: int = 15,
    off_peak_price: float = 0.15,
    peak_price: float = 0.35,
    export_price: float = 0.05,
) -> pd.DataFrame:
    """
    Generate Time-of-Use (TOU) electricity pricing [EUR/kWh].

    Off-peak: 22:00 - 07:00
    Peak:     07:00 - 22:00
    Export:   Contractual feed-in tariff
    """
    steps_per_day = int(24 * 60 / resolution_min)
    total_steps = n_days * steps_per_day
    dt_hours = resolution_min / 60.0

    time_hours = np.arange(total_steps) * dt_hours
    hour_of_day = time_hours % 24.0

    is_peak = (hour_of_day >= 7.0) & (hour_of_day < 22.0)
    import_price = np.where(is_peak, peak_price, off_peak_price)
    export_tariff = np.full(total_steps, export_price)

    return pd.DataFrame(
        {
            "time_hours": time_hours,
            "hour_of_day": hour_of_day,
            "import_price": import_price,
            "export_price": export_tariff,
            "is_peak": is_peak,
        }
    )


def generate_representative_days(
    resolution_min: int = 15,
) -> dict:
    """
    Generate 4 seasonal representative operating days for optimal sizing (opt_5).

    Returns
    -------
    dict with:
      - 'profiles': DataFrame containing PV potential (normalized to 1 kWp) and Load [kW]
      - 'weights': dict mapping day name to annual weight (sum = 365 days)
      - 'day_names': list of names
    """
    steps_per_day = int(24 * 60 / resolution_min)
    dt_hours = resolution_min / 60.0
    t = np.arange(steps_per_day) * dt_hours

    sin_summer = np.where((t >= 5.5) & (t <= 20.5), np.clip(np.sin(np.pi * (t - 5.5) / 15.0), 0.0, 1.0), 0.0)
    pv_summer_sunny = 0.95 * (sin_summer ** 1.1)
    load_summer_sunny = 1.2 + 1.2 * np.exp(-0.5 * ((t - 8) / 1.5) ** 2) + 2.0 * np.exp(-0.5 * ((t - 20) / 2) ** 2)

    # 2. Summer Cloudy: medium solar with cloud dips, modest load
    pv_summer_cloudy = np.where(
        (t >= 6.0) & (t <= 20.0),
        0.45 * (np.sin(np.pi * (t - 6.0) / 14.0)) * (0.6 + 0.4 * np.cos(3 * np.pi * t / 24)),
        0.0,
    )
    pv_summer_cloudy = np.clip(pv_summer_cloudy, 0, 1)
    load_summer_cloudy = 1.3 + 1.4 * np.exp(-0.5 * ((t - 8.5) / 1.5) ** 2) + 2.2 * np.exp(-0.5 * ((t - 19.5) / 2) ** 2)

    # 3. Winter Sunny: low/short solar (peak 0.50 kW/kWp, 08:30-16:30), high heating load
    pv_winter_sunny = np.where(
        (t >= 8.5) & (t <= 16.5),
        0.50 * (np.sin(np.pi * (t - 8.5) / 8.0)),
        0.0,
    )
    load_winter_sunny = 2.5 + 2.2 * np.exp(-0.5 * ((t - 8) / 1.5) ** 2) + 3.8 * np.exp(-0.5 * ((t - 19) / 2.2) ** 2)

    # 4. Winter Cloudy: very low solar (overcast), high heating load
    pv_winter_cloudy = np.where(
        (t >= 9.0) & (t <= 16.0),
        0.12 * (np.sin(np.pi * (t - 9.0) / 7.0)),
        0.0,
    )
    load_winter_cloudy = 2.8 + 2.5 * np.exp(-0.5 * ((t - 7.5) / 1.5) ** 2) + 4.2 * np.exp(-0.5 * ((t - 18.5) / 2.2) ** 2)

    weights = {
        "summer_sunny": 120,   # ~4 months
        "summer_cloudy": 60,   # ~2 months
        "winter_sunny": 65,    # ~2 months
        "winter_cloudy": 120,  # ~4 months
    }

    days = {
        "summer_sunny": {"pv": pv_summer_sunny, "load": load_summer_sunny},
        "summer_cloudy": {"pv": pv_summer_cloudy, "load": load_summer_cloudy},
        "winter_sunny": {"pv": pv_winter_sunny, "load": load_winter_sunny},
        "winter_cloudy": {"pv": pv_winter_cloudy, "load": load_winter_cloudy},
    }

    return {
        "time_hours": t,
        "days": days,
        "weights": weights,
        "resolution_min": resolution_min,
        "steps_per_day": steps_per_day,
    }
