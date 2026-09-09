"""
2_opt_3_forecasting.py
======================
Deterministic and probabilistic forecasting for microgrids.
Course: ELEN0445 - Microgrids, Université de Liège.
Slide deck: opt_3_forecasting

Illustrates:
1. Baseline persistence model (Slide 393).
2. Seasonal persistence model (24-hour lag).
3. Autoregressive and calendar feature linear regression.
4. Direct vs. Recursive multi-step forecasting strategies (Slides 408-456).
5. Error metrics vs. lead time k: Bias, MAE, RMSE, NMAE, NRMSE (Slides 582-616).
6. Probabilistic forecasting via quantile regression / pinball loss (Slides 664-676).
7. Evaluation of sharpness and calibration (reliability).
"""

import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib_cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import linprog

import common_data


# =============================================================================
# 1. Error Metrics - Slides 560-610
# =============================================================================

def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, p_nom: float = 10.0) -> dict:
    """
    Computes standard forecasting error scores:
      - error = y_true - y_pred
      - bias  = mean(error)
      - MAE   = mean(|error|)
      - RMSE  = sqrt(mean(error^2))
      - NMAE  = MAE / P_nom
      - NRMSE = RMSE / P_nom
    """
    err = y_true - y_pred
    bias = np.mean(err)
    mae = np.mean(np.abs(err))
    rmse = np.sqrt(np.mean(err ** 2))
    nmae = mae / p_nom
    nrmse = rmse / p_nom

    return {
        "bias": bias,
        "mae": mae,
        "rmse": rmse,
        "nmae": nmae,
        "nrmse": nrmse,
    }


# =============================================================================
# 2. Linear Quantile Regression via Pinball Loss LP - Slide 664-676
# =============================================================================

def fit_quantile_regression(X: np.ndarray, y: np.ndarray, tau: float) -> np.ndarray:
    """
    Solves linear quantile regression for quantile tau in (0, 1) using LP.
      min sum_i [ tau * u_i^+ + (1 - tau) * u_i^- ]
      s.t. y_i - X_i * beta = u_i^+ - u_i^-
           u_i^+ >= 0, u_i^- >= 0
    Variables: [beta (free), u^+ (>=0), u^- (>=0)]
    """
    n_samples, n_features = X.shape

    # Objective: 0 on beta, tau on u^+, (1-tau) on u^-
    c = np.concatenate([
        np.zeros(n_features),
        tau * np.ones(n_samples),
        (1.0 - tau) * np.ones(n_samples),
    ])

    # Equality constraint: X * beta + u^+ - u^- = y
    A_eq = np.hstack([X, np.eye(n_samples), -np.eye(n_samples)])
    b_eq = y

    # Bounds: beta is free (-inf, inf), u^+ >= 0, u^- >= 0
    bounds = [(None, None)] * n_features + [(0.0, None)] * (2 * n_samples)

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(f"Quantile regression failed: {res.message}")

    beta = res.x[:n_features]
    return beta


# =============================================================================
# 3. Main Forecasting Experiment
# =============================================================================

def run_forecasting_pipeline():
    print("\n" + "=" * 70)
    print("RUNNING FORECASTING PIPELINE (PV & Load)")
    print("=" * 70)

    # 1. Generate 4 weeks of synthetic data (28 days at 15-min resolution)
    res_min = 15
    steps_per_day = int(24 * 60 / res_min) # 96 steps
    n_days = 28
    p_nom_pv = 10.0 # Nominal PV capacity [kWp]

    df_pv = common_data.generate_synthetic_pv(n_days=n_days, resolution_min=res_min, peak_kw=p_nom_pv, cloudiness=0.35, seed=77)
    df_load = common_data.generate_synthetic_load(n_days=n_days, resolution_min=res_min, base_kw=1.5, peak_kw=6.5, seed=88)

    y_pv_series = df_pv["pv_potential_kw"].values
    hour_series = df_pv["hour_of_day"].values

    # Train / Test split: 21 days training, 7 days testing (Forward Chaining / Time-Order CV, Slide 491)
    train_end = 21 * steps_per_day
    train_idx = np.arange(train_end)
    test_idx = np.arange(train_end, len(y_pv_series))

    print(f"Dataset: {n_days} days ({len(y_pv_series)} steps of {res_min} min)")
    print(f"Train set: {len(train_idx)} steps (first 3 weeks)")
    print(f"Test set:  {len(test_idx)} steps (last 1 week)\n")

    # Feature engineering for ML model:
    # Lags: y(t), y(t-1), y(t-2), y(t-24h)
    # Calendar: sin/cos of hour of day
    def build_features(series, hours):
        N = len(series)
        X_mat = []
        y_targets = []
        valid_indices = []

        lag_24h = steps_per_day
        for t in range(lag_24h, N):
            feats = [
                1.0, # Intercept
                series[t],          # Lag 0 (current known value)
                series[t - 1],      # Lag 1
                series[t - 2],      # Lag 2
                series[t - lag_24h], # Lag 24h
                np.sin(2 * np.pi * hours[t] / 24.0),
                np.cos(2 * np.pi * hours[t] / 24.0),
            ]
            X_mat.append(feats)
            y_targets.append(series[t])
            valid_indices.append(t)

        return np.array(X_mat), np.array(y_targets), np.array(valid_indices)

    # =========================================================================
    # Multi-Step Evaluation over Horizons k = 1 to 24 hours (Slide 408)
    # =========================================================================
    max_k_hours = 24
    k_steps_eval = [1, 2, 4, 8, 12, 16, 20, 24] # in hours
    k_indices = [int(h * 60 / res_min) for h in k_steps_eval]

    metrics_persistence = []
    metrics_seasonal = []
    metrics_direct_ml = []

    print("-" * 70)
    print("EVALUATING FORECASTING MODELS ACROSS LEAD TIMES (k)")
    print("-" * 70)

    # Pre-train Direct ML models for each lead time k
    # Target for direct model: y(t + k)
    direct_weights = {}
    lag_24h = steps_per_day

    # Training features
    train_valid = train_idx[train_idx >= lag_24h]

    for k_step in k_indices:
        # Build training set for lead time k
        X_tr, y_tr = [], []
        for t in train_valid:
            if t + k_step < train_end:
                feats = [
                    1.0,
                    y_pv_series[t],
                    y_pv_series[t - 1],
                    y_pv_series[t - 2],
                    y_pv_series[t - lag_24h],
                    np.sin(2 * np.pi * hour_series[t + k_step] / 24.0),
                    np.cos(2 * np.pi * hour_series[t + k_step] / 24.0),
                ]
                X_tr.append(feats)
                y_tr.append(y_pv_series[t + k_step])

        X_tr = np.array(X_tr)
        y_tr = np.array(y_tr)
        # OLS fit: beta = (X^T X)^-1 X^T y
        beta = np.linalg.lstsq(X_tr, y_tr, rcond=None)[0]
        direct_weights[k_step] = beta

    # Evaluate on Test Set
    test_start = test_idx[0]
    test_end = test_idx[-1]

    for h_hours, k_step in zip(k_steps_eval, k_indices):
        y_true_list = []
        y_pers_list = []
        y_seas_list = []
        y_dir_list = []

        beta = direct_weights[k_step]

        for t in range(test_start, test_end - k_step):
            y_actual = y_pv_series[t + k_step]
            # 1. Persistence: y_hat(t+k) = y(t)
            y_pers = y_pv_series[t]
            # 2. Seasonal Persistence: y_hat(t+k) = y(t+k - 24h)
            y_seas = y_pv_series[t + k_step - lag_24h]
            # 3. Direct ML
            feats = [
                1.0,
                y_pv_series[t],
                y_pv_series[t - 1],
                y_pv_series[t - 2],
                y_pv_series[t - lag_24h],
                np.sin(2 * np.pi * hour_series[t + k_step] / 24.0),
                np.cos(2 * np.pi * hour_series[t + k_step] / 24.0),
            ]
            y_dir = max(0.0, np.dot(feats, beta))

            y_true_list.append(y_actual)
            y_pers_list.append(y_pers)
            y_seas_list.append(y_seas)
            y_dir_list.append(y_dir)

        y_true_arr = np.array(y_true_list)
        m_pers = compute_metrics(y_true_arr, np.array(y_pers_list), p_nom=p_nom_pv)
        m_seas = compute_metrics(y_true_arr, np.array(y_seas_list), p_nom=p_nom_pv)
        m_dir  = compute_metrics(y_true_arr, np.array(y_dir_list), p_nom=p_nom_pv)

        metrics_persistence.append((h_hours, m_pers))
        metrics_seasonal.append((h_hours, m_seas))
        metrics_direct_ml.append((h_hours, m_dir))

    # Print Summary Table
    rows = []
    for h, m_p, m_s, m_d in zip(k_steps_eval, metrics_persistence, metrics_seasonal, metrics_direct_ml):
        rows.append({
            "Horizon": f"{h} h",
            "Persistence NMAE (%)": f"{m_p[1]['nmae']*100:.2f}%",
            "Seasonal NMAE (%)": f"{m_s[1]['nmae']*100:.2f}%",
            "Direct ML NMAE (%)": f"{m_d[1]['nmae']*100:.2f}%",
            "Direct ML NRMSE (%)": f"{m_d[1]['nrmse']*100:.2f}%",
            "ML Skill vs. Naive": f"{(1.0 - m_d[1]['nmae'] / m_p[1]['nmae'])*100:.1f}%",
        })
    df_metrics = pd.DataFrame(rows)
    print(df_metrics.to_string(index=False))

    # =========================================================================
    # 4. Probabilistic Quantile Forecasting (Slide 664-676)
    # =========================================================================
    print("\n" + "-" * 70)
    print("PROBABILISTIC QUANTILE FORECASTING (Pinball Loss Optimization)")
    print("-" * 70)

    # Fit 1-step-ahead (15-min) quantiles: tau = 0.10, 0.50, 0.90
    X_tr_q, y_tr_q = [], []
    for t in train_valid:
        if t + 1 < train_end:
            feats = [
                1.0,
                y_pv_series[t],
                y_pv_series[t - 1],
                y_pv_series[t - lag_24h],
                np.sin(2 * np.pi * hour_series[t + 1] / 24.0),
                np.cos(2 * np.pi * hour_series[t + 1] / 24.0),
            ]
            X_tr_q.append(feats)
            y_tr_q.append(y_pv_series[t + 1])
    X_tr_q = np.array(X_tr_q)
    y_tr_q = np.array(y_tr_q)

    beta_q10 = fit_quantile_regression(X_tr_q, y_tr_q, tau=0.10)
    beta_q50 = fit_quantile_regression(X_tr_q, y_tr_q, tau=0.50)
    beta_q90 = fit_quantile_regression(X_tr_q, y_tr_q, tau=0.90)

    # Test on test set
    X_te_q, y_te_q = [], []
    for t in range(test_start, test_end - 1):
        feats = [
            1.0,
            y_pv_series[t],
            y_pv_series[t - 1],
            y_pv_series[t - lag_24h],
            np.sin(2 * np.pi * hour_series[t + 1] / 24.0),
            np.cos(2 * np.pi * hour_series[t + 1] / 24.0),
        ]
        X_te_q.append(feats)
        y_te_q.append(y_pv_series[t + 1])
    X_te_q = np.array(X_te_q)
    y_te_q = np.array(y_te_q)

    q10_pred = np.clip(np.dot(X_te_q, beta_q10), 0, p_nom_pv)
    q50_pred = np.clip(np.dot(X_te_q, beta_q50), 0, p_nom_pv)
    q90_pred = np.clip(np.dot(X_te_q, beta_q90), 0, p_nom_pv)

    # Ensure quantile monotonicity: q10 <= q50 <= q90
    q50_pred = np.maximum(q50_pred, q10_pred)
    q90_pred = np.maximum(q90_pred, q50_pred)

    # Reliability / Calibration check (Slide 678):
    # Nominal 80% coverage interval [q10, q90]
    covered = (y_te_q >= q10_pred) & (y_te_q <= q90_pred)
    empirical_coverage = np.mean(covered) * 100.0
    avg_sharpness = np.mean(q90_pred - q10_pred) # Width of prediction interval

    print(f"Quantile Regression Results on Test Set (1-step lead time):")
    print(f"  Target coverage:      80.0%  (Interval [q0.10, q0.90])")
    print(f"  Empirical coverage:   {empirical_coverage:.1f}% (Calibration check)")
    print(f"  Average sharpness:    {avg_sharpness:.2f} kW (Mean interval width)")

    # =========================================================================
    # 5. Generate Multi-Panel Figures (Matching Slides 616 and 678)
    # =========================================================================
    fig = plt.figure(figsize=(14, 10))

    # Subplot 1: Time Series Forecast Tracking over 2 Test Days
    ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)
    view_steps = 2 * steps_per_day
    t_plot = np.arange(view_steps) * (res_min / 60.0)
    ax1.plot(t_plot, y_te_q[:view_steps], "k-", linewidth=1.5, label="Actual PV Production")
    ax1.plot(t_plot, q50_pred[:view_steps], "b--", linewidth=1.5, label="Median Forecast (q0.50)")
    ax1.fill_between(
        t_plot, q10_pred[:view_steps], q90_pred[:view_steps],
        color="royalblue", alpha=0.3, label="80% Prediction Interval [q0.10, q0.90]"
    )
    ax1.set_title("Probabilistic PV Forecast on Unseen Test Days (Slide 664)", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Time [hours]")
    ax1.set_ylabel("Power [kW]")
    ax1.set_xlim(0, 48)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper right")

    # Subplot 2: Score Comparison vs Lead Time k (Slide 616)
    ax2 = plt.subplot2grid((2, 2), (1, 0))
    horizons = k_steps_eval
    nmae_pers = [m[1]["nmae"] * 100 for m in metrics_persistence]
    nmae_seas = [m[1]["nmae"] * 100 for m in metrics_seasonal]
    nmae_ml   = [m[1]["nmae"] * 100 for m in metrics_direct_ml]
    nrmse_ml  = [m[1]["nrmse"] * 100 for m in metrics_direct_ml]

    ax2.plot(horizons, nmae_pers, "r-o", label="Persistence NMAE")
    ax2.plot(horizons, nmae_seas, "g-s", label="Seasonal Persistence NMAE")
    ax2.plot(horizons, nmae_ml, "b-^", label="Direct ML NMAE")
    ax2.plot(horizons, nrmse_ml, "b--^", label="Direct ML NRMSE")
    ax2.set_title("Error Scores vs. Lead Time $k$ (Slide 616)", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Lead Time $k$ [hours]")
    ax2.set_ylabel("Normalized Error [% of P_nom]")
    ax2.set_xticks(horizons)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper left")

    # Subplot 3: Forecast Error Histogram & Bias
    ax3 = plt.subplot2grid((2, 2), (1, 1))
    errors = y_te_q - q50_pred
    ax3.hist(errors, bins=40, color="teal", edgecolor="black", alpha=0.7, density=True)
    ax3.axvline(np.mean(errors), color="red", linestyle="--", linewidth=2, label=f"Bias = {np.mean(errors):.3f} kW")
    ax3.set_title("Forecast Error Distribution $\\varepsilon_{t+k|t}$ (Slide 568)", fontsize=11, fontweight="bold")
    ax3.set_xlabel("Forecast Error [kW]")
    ax3.set_ylabel("Probability Density")
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc="upper left")

    plt.tight_layout()
    plot_path = "examples/opt_3_forecasting_evaluation.png"
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"\nFigure saved successfully to: {plot_path}")


if __name__ == "__main__":
    run_forecasting_pipeline()
