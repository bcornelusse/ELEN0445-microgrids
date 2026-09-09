"""
1_opt_2_real_time.py
====================
Real-time optimization in microgrids.
Course: ELEN0445 - Microgrids, Université de Liège.
Slide deck: opt_2_RT

Illustrates:
1. Rule-Based Controller (RBC) from Slide 151.
2. Exact test cases from Slide 213 (green, red, blue points).
3. Optimization-Based Controller Problem (1) from Slide 224 (demonstrating infeasibility on overload).
4. Feasibility Formulation Problem (2) with slack variables from Slide 269.
5. Battery SoC tracking with separate charge/discharge efficiencies from Slide 304.
6. Grid-connected extension with import/export tariffs from Slide 343.
7. Full 24-hour simulation comparing dispatch profiles, curtailment, and operational costs.
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
# 1. Rule-Based Controller (RBC) - Slide 151
# =============================================================================

def rule_based_controller(
    p_load: float,
    p_pv_max: float,
    p_bat_charge_max: float,   # P_bat_underline >= 0 (max power battery can ABSORB)
    p_bat_discharge_max: float, # P_bat_overline >= 0 (max power battery can INJECT)
    p_gen_max: float,
) -> tuple[dict, float]:
    """
    Implements the RBC algorithm from slide 151:
    Inputs:
      - p_load: electric demand [kW]
      - p_pv_max: maximum available PV generation [kW]
      - p_bat_charge_max: maximum charge power [kW] (positive quantity)
      - p_bat_discharge_max: maximum discharge power [kW] (positive quantity)
      - p_gen_max: maximum generator power [kW]

    Convention:
      - p_bat > 0: discharging (injecting into microgrid)
      - p_bat < 0: charging (absorbing from microgrid)

    Returns:
      - setpoints: dict(p_pv, p_bat, p_gen)
      - delta: remaining unbalance (delta > 0 indicates unserved load)
    """
    delta = p_load - p_pv_max

    if delta > 0:
        # Excess load: discharge battery first, then use generator
        p_pv = p_pv_max
        if p_bat_discharge_max > delta:
            p_bat = delta
            p_gen = 0.0
            delta = 0.0
        else:
            p_bat = p_bat_discharge_max
            delta -= p_bat
            if p_gen_max > delta:
                p_gen = delta
                delta = 0.0
            else:
                p_gen = p_gen_max
                delta -= p_gen  # Unserved load
    else:
        # Excess PV: charge battery first, then curtail
        p_gen = 0.0
        if p_bat_charge_max > -delta:
            p_bat = delta  # negative value -> charging
            p_pv = p_pv_max
            delta = 0.0
        else:
            p_bat = -p_bat_charge_max
            delta -= p_bat
            p_pv = p_pv_max + delta  # Curtail excess PV
            delta = 0.0

    return {"p_pv": p_pv, "p_bat": p_bat, "p_gen": p_gen}, delta


# =============================================================================
# 2. Optimization-Based Controller: Problem (1) - Slide 224
# =============================================================================

def solve_rt_problem_1(
    p_load: float,
    p_pv_max: float,
    p_bat_charge_max: float,
    p_bat_discharge_max: float,
    p_gen_max: float,
    pi_gen: float = 0.50,
    epsilon: float = 0.01,
) -> dict:
    """
    Formulation (Slide 224):
      min   pi_gen * p_gen + epsilon * p_bat
      s.t.  p_pv + p_bat + p_gen = p_load
            0 <= p_pv <= p_pv_max
            -p_bat_charge_max <= p_bat <= p_bat_discharge_max
            0 <= p_gen <= p_gen_max

    Decision vector x = [p_pv, p_bat, p_gen]^T
    """
    # Objective: c^T x
    c = np.array([0.0, epsilon, pi_gen])

    # Equality constraint: [1, 1, 1] * x = p_load
    A_eq = np.array([[1.0, 1.0, 1.0]])
    b_eq = np.array([p_load])

    # Bounds on variables
    bounds = [
        (0.0, p_pv_max),
        (-p_bat_charge_max, p_bat_discharge_max),
        (0.0, p_gen_max),
    ]

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if res.success:
        return {
            "success": True,
            "p_pv": res.x[0],
            "p_bat": res.x[1],
            "p_gen": res.x[2],
            "cost": res.fun,
            "status": res.message,
        }
    else:
        return {
            "success": False,
            "p_pv": np.nan,
            "p_bat": np.nan,
            "p_gen": np.nan,
            "cost": np.nan,
            "status": res.message,
        }


# =============================================================================
# 3. Feasibility Formulation: Problem (2) with Slacks - Slide 269
# =============================================================================

def solve_rt_problem_2_slacks(
    p_load: float,
    p_pv_max: float,
    p_bat_charge_max: float,
    p_bat_discharge_max: float,
    p_gen_max: float,
    pi_gen: float = 0.50,
    epsilon: float = 0.01,
    penalty_v: float = 1000.0,
) -> dict:
    """
    Formulation with slacks (Slide 269):
      min   pi_gen * p_gen + epsilon * p_bat + V * (p_plus + p_minus)
      s.t.  p_pv + p_bat + p_gen + p_minus = p_load + p_plus
            0 <= p_pv <= p_pv_max
            -p_bat_charge_max <= p_bat <= p_bat_discharge_max
            0 <= p_gen <= p_gen_max
            p_plus >= 0 (curtailment / excess)
            p_minus >= 0 (load shedding)

    Decision vector x = [p_pv, p_bat, p_gen, p_plus, p_minus]^T
    """
    c = np.array([0.0, epsilon, pi_gen, penalty_v, penalty_v])

    # Equality: p_pv + p_bat + p_gen - p_plus + p_minus = p_load
    A_eq = np.array([[1.0, 1.0, 1.0, -1.0, 1.0]])
    b_eq = np.array([p_load])

    bounds = [
        (0.0, p_pv_max),
        (-p_bat_charge_max, p_bat_discharge_max),
        (0.0, p_gen_max),
        (0.0, None),
        (0.0, None),
    ]

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if res.success:
        return {
            "success": True,
            "p_pv": res.x[0],
            "p_bat": res.x[1],
            "p_gen": res.x[2],
            "p_plus": res.x[3],
            "p_minus": res.x[4],
            "cost": res.fun,
            "status": res.message,
        }
    else:
        raise RuntimeError(f"Problem (2) failed unexpectedly: {res.message}")


# =============================================================================
# 4. Grid-Connected Extension - Slide 343
# =============================================================================

def solve_rt_grid_connected(
    p_load: float,
    p_pv_max: float,
    p_bat_charge_max: float,
    p_bat_discharge_max: float,
    p_gen_max: float,
    p_grid_import_max: float = 10.0,
    p_grid_export_max: float = 10.0,
    pi_import: float = 0.30,
    pi_export: float = 0.05,
    pi_gen: float = 0.50,
    epsilon: float = 0.01,
    penalty_v: float = 1000.0,
) -> dict:
    """
    Grid-connected formulation (Slide 343):
      min   pi_gen * p_gen + epsilon * p_bat + pi_imp * p_imp - pi_exp * p_exp + V * (p_plus + p_minus)
      s.t.  p_pv + p_bat + p_gen + p_imp + p_minus = p_load + p_exp + p_plus
    Decision vector x = [p_pv, p_bat, p_gen, p_imp, p_exp, p_plus, p_minus]^T
    """
    c = np.array([0.0, epsilon, pi_gen, pi_import, -pi_export, penalty_v, penalty_v])

    # Equality: p_pv + p_bat + p_gen + p_imp - p_exp - p_plus + p_minus = p_load
    A_eq = np.array([[1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0]])
    b_eq = np.array([p_load])

    bounds = [
        (0.0, p_pv_max),
        (-p_bat_charge_max, p_bat_discharge_max),
        (0.0, p_gen_max),
        (0.0, p_grid_import_max),
        (0.0, p_grid_export_max),
        (0.0, None),
        (0.0, None),
    ]

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if res.success:
        return {
            "success": True,
            "p_pv": res.x[0],
            "p_bat": res.x[1],
            "p_gen": res.x[2],
            "p_imp": res.x[3],
            "p_exp": res.x[4],
            "p_plus": res.x[5],
            "p_minus": res.x[6],
            "cost": res.fun,
        }
    else:
        raise RuntimeError(f"Grid LP failed: {res.message}")


# =============================================================================
# 5. Slide 213 Graphical Verification
# =============================================================================

def verify_slide_213_test_points():
    """
    Reproduces the three test points from Slide 213:
      - Green: (P_load=0.5, P_pv_max=4.0)
      - Red:   (P_load=4.0, P_pv_max=5.0)
      - Blue:  (P_load=8.0, P_pv_max=4.0)
    With assumptions from slide:
      - P_bat_charge_max = 2.0 kW
      - P_bat_discharge_max = 2.0 kW
      - P_gen_max = 5.0 kW
    """
    print("\n" + "=" * 70)
    print("SLIDE 213: TEST POINTS VERIFICATION (RBC vs. Optimization)")
    print("=" * 70)

    test_points = [
        ("Green point (Excess PV > Bat charge capacity)", 0.5, 4.0),
        ("Red point   (Excess PV < Bat charge capacity)", 4.0, 5.0),
        ("Blue point  (Deficit load > Bat discharge capacity)", 8.0, 4.0),
    ]

    p_bat_ch_max = 2.0
    p_bat_dis_max = 2.0
    p_gen_max = 5.0

    print(f"Parameters: P_bat_ch_max={p_bat_ch_max} kW, P_bat_dis_max={p_bat_dis_max} kW, P_gen_max={p_gen_max} kW\n")

    for name, p_load, p_pv in test_points:
        rbc_res, delta = rule_based_controller(p_load, p_pv, p_bat_ch_max, p_bat_dis_max, p_gen_max)
        lp_res = solve_rt_problem_2_slacks(p_load, p_pv, p_bat_ch_max, p_bat_dis_max, p_gen_max)

        print(f"--- {name}: P_load = {p_load:.1f} kW, P_pv_max = {p_pv:.1f} kW ---")
        print(f"  RBC:      p_pv = {rbc_res['p_pv']:.2f} kW, p_bat = {rbc_res['p_bat']:.2f} kW, p_gen = {rbc_res['p_gen']:.2f} kW, unbalance = {delta:.2f} kW")
        print(f"  LP (P2):  p_pv = {lp_res['p_pv']:.2f} kW, p_bat = {lp_res['p_bat']:.2f} kW, p_gen = {lp_res['p_gen']:.2f} kW, shed = {lp_res['p_minus']:.2f} kW")
        assert np.isclose(rbc_res["p_pv"], lp_res["p_pv"], atol=1e-3)
        assert np.isclose(rbc_res["p_bat"], lp_res["p_bat"], atol=1e-3)
        assert np.isclose(rbc_res["p_gen"], lp_res["p_gen"], atol=1e-3)
        print("  -> Exact match between RBC and LP optimal dispatch!\n")


# =============================================================================
# 6. Full Day 24-Hour Simulation
# =============================================================================

def run_day_simulation():
    """
    Simulates a 24-hour operation (15-min resolution, 96 steps) comparing:
      1. RBC (Off-Grid)
      2. Problem (2) LP (Off-Grid)
      3. Problem (1) LP showing infeasibility when stress-tested
      4. Problem (2) LP (Grid-Connected)
    Includes battery state of charge dynamics with charge/discharge efficiencies (Slide 304).
    """
    print("\n" + "=" * 70)
    print("RUNNING 24-HOUR TIME-SERIES SIMULATION")
    print("=" * 70)

    # 1. Generate synthetic profile
    res_min = 15
    dt_hours = res_min / 60.0
    n_steps = int(24 * 60 / res_min)

    df_pv = common_data.generate_synthetic_pv(n_days=1, resolution_min=res_min, peak_kw=8.0, cloudiness=0.3, seed=42)
    df_load = common_data.generate_synthetic_load(n_days=1, resolution_min=res_min, base_kw=1.2, peak_kw=5.5, seed=105)
    df_tou = common_data.generate_tou_tariffs(n_days=1, resolution_min=res_min, off_peak_price=0.18, peak_price=0.36, export_price=0.06)

    # Microgrid physical parameters
    bat_capacity_kwh = 12.0
    soc_min = 0.20 * bat_capacity_kwh  # 2.4 kWh
    soc_max = 0.95 * bat_capacity_kwh  # 11.4 kWh
    soc_init = 0.50 * bat_capacity_kwh # 6.0 kWh

    eta_charge = 0.95
    eta_discharge = 0.95
    p_bat_inv_max = 4.0  # Max power rating of inverter [kW]
    p_gen_max = 4.0      # Backup genset [kW]
    pi_gen = 0.45        # Fuel cost [EUR/kWh]
    epsilon = 0.005      # Battery degradation/preference fee [EUR/kWh]

    # Arrays to store trajectories
    time_h = df_pv["time_hours"].values
    pv_avail = df_pv["pv_potential_kw"].values.copy()
    load = df_load["load_kw"].values.copy()

    # Let's add a high-demand spike at 20:00 to test capacity limits
    spike_idx = int(20.0 / dt_hours)
    load[spike_idx : spike_idx + 3] += 3.5  # Creates potential overload to demonstrate shedding

    def simulate_controller(controller_type: str):
        soc = soc_init
        records = []

        for t in range(n_steps):
            p_l = load[t]
            p_pv_max = pv_avail[t]

            # Dynamic battery power limits based on current SoC and inverter capacity
            # Max discharge: limited by current stored energy above soc_min
            p_dis_max = min(p_bat_inv_max, (soc - soc_min) * eta_discharge / dt_hours)
            p_dis_max = max(0.0, p_dis_max)

            # Max charge: limited by room up to soc_max
            p_ch_max = min(p_bat_inv_max, (soc_max - soc) / (eta_charge * dt_hours))
            p_ch_max = max(0.0, p_ch_max)

            if controller_type == "RBC":
                setpoints, delta = rule_based_controller(p_l, p_pv_max, p_ch_max, p_dis_max, p_gen_max)
                rec = {
                    "p_pv": setpoints["p_pv"],
                    "p_bat": setpoints["p_bat"],
                    "p_gen": setpoints["p_gen"],
                    "p_imp": 0.0,
                    "p_exp": 0.0,
                    "p_curtail": p_pv_max - setpoints["p_pv"],
                    "p_shed": delta,
                }
            elif controller_type == "LP_OffGrid":
                res = solve_rt_problem_2_slacks(
                    p_l, p_pv_max, p_ch_max, p_dis_max, p_gen_max,
                    pi_gen=pi_gen, epsilon=epsilon
                )
                rec = {
                    "p_pv": res["p_pv"],
                    "p_bat": res["p_bat"],
                    "p_gen": res["p_gen"],
                    "p_imp": 0.0,
                    "p_exp": 0.0,
                    "p_curtail": res["p_plus"],
                    "p_shed": res["p_minus"],
                }
            elif controller_type == "LP_Grid":
                res = solve_rt_grid_connected(
                    p_l, p_pv_max, p_ch_max, p_dis_max, p_gen_max,
                    p_grid_import_max=6.0, p_grid_export_max=6.0,
                    pi_import=df_tou["import_price"].iloc[t],
                    pi_export=df_tou["export_price"].iloc[t],
                    pi_gen=pi_gen, epsilon=epsilon,
                )
                rec = {
                    "p_pv": res["p_pv"],
                    "p_bat": res["p_bat"],
                    "p_gen": res["p_gen"],
                    "p_imp": res["p_imp"],
                    "p_exp": res["p_exp"],
                    "p_curtail": res["p_plus"],
                    "p_shed": res["p_minus"],
                }
            else:
                raise ValueError(controller_type)

            # Update battery SoC with efficiencies (Slide 304)
            p_bat = rec["p_bat"]
            if p_bat < 0:  # Charging
                soc += (-p_bat) * eta_charge * dt_hours
            else:          # Discharging
                soc -= (p_bat / eta_discharge) * dt_hours
            soc = np.clip(soc, soc_min, soc_max)

            rec["soc_kwh"] = soc
            rec["soc_pct"] = (soc / bat_capacity_kwh) * 100.0
            records.append(rec)

        return pd.DataFrame(records)

    df_rbc = simulate_controller("RBC")
    df_lp_off = simulate_controller("LP_OffGrid")
    df_lp_grid = simulate_controller("LP_Grid")

    # Verify Problem (1) infeasibility behavior on overload step
    p_load_overload = load[spike_idx]
    p_dis_max_test = 2.0
    p_pv_test = pv_avail[spike_idx]
    res_p1 = solve_rt_problem_1(p_load_overload, p_pv_test, 2.0, p_dis_max_test, p_gen_max)
    print(f"\nStress Test for Problem (1) at peak hour t=20:00 (Load={p_load_overload:.2f} kW, Capacity={p_pv_test+p_dis_max_test+p_gen_max:.2f} kW):")
    print(f"  Problem (1) success: {res_p1['success']} -> Status: {res_p1['status']}")
    print("  -> Problem (1) fails when load exceeds capacity; Problem (2) with slacks resolves this gracefully!\n")

    # Metrics Summary
    def calc_metrics(df_sim, name):
        fuel_cost = (df_sim["p_gen"] * dt_hours * pi_gen).sum()
        grid_cost = (df_sim["p_imp"] * dt_hours * df_tou["import_price"]).sum() - (df_sim["p_exp"] * dt_hours * df_tou["export_price"]).sum()
        total_curtail_kwh = (df_sim["p_curtail"] * dt_hours).sum()
        total_shed_kwh = (df_sim["p_shed"] * dt_hours).sum()
        bat_throughput_kwh = (np.abs(df_sim["p_bat"]) * dt_hours).sum() / 2.0
        return {
            "Controller": name,
            "Fuel Cost (EUR)": f"{fuel_cost:.2f}",
            "Grid Cost (EUR)": f"{grid_cost:.2f}",
            "Total Cost (EUR)": f"{fuel_cost + grid_cost:.2f}",
            "PV Curtailed (kWh)": f"{total_curtail_kwh:.2f}",
            "Unserved Load (kWh)": f"{total_shed_kwh:.2f}",
            "Battery Throughput (kWh)": f"{bat_throughput_kwh:.2f}",
        }

    summary = [
        calc_metrics(df_rbc, "Rule-Based Controller (Off-Grid)"),
        calc_metrics(df_lp_off, "Optimization Problem 2 (Off-Grid)"),
        calc_metrics(df_lp_grid, "Optimization Problem 2 (Grid-Tied)"),
    ]
    df_summary = pd.DataFrame(summary)
    print(df_summary.to_string(index=False))

    # =============================================================================
    # 7. Generate Multi-Panel Comparison Plot
    # =============================================================================
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # Subplot 1: Off-grid RBC Dispatch
    axes[0].plot(time_h, load, "k--", label="Load Demand", linewidth=1.8)
    axes[0].plot(time_h, pv_avail, "gold", label="PV Potential", alpha=0.6)
    axes[0].step(time_h, df_rbc["p_pv"], color="orange", label="PV Used", where="mid")
    axes[0].step(time_h, df_rbc["p_bat"], color="teal", label="Battery Power (+dis / -ch)", where="mid")
    axes[0].step(time_h, df_rbc["p_gen"], color="firebrick", label="Diesel Generator", where="mid")
    axes[0].fill_between(time_h, 0, df_rbc["p_shed"], color="red", alpha=0.3, label="Load Shed")
    axes[0].set_title("Off-Grid Rule-Based Controller (RBC - Slide 151)", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Power [kW]")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc="upper left", ncol=3, fontsize=8)

    # Subplot 2: Grid-Tied Optimization Dispatch
    axes[1].plot(time_h, load, "k--", label="Load Demand", linewidth=1.8)
    axes[1].step(time_h, df_lp_grid["p_pv"], color="orange", label="PV Used", where="mid")
    axes[1].step(time_h, df_lp_grid["p_bat"], color="teal", label="Battery Power", where="mid")
    axes[1].step(time_h, df_lp_grid["p_imp"], color="blue", label="Grid Import", where="mid")
    axes[1].step(time_h, df_lp_grid["p_exp"], color="green", label="Grid Export", where="mid")
    axes[1].set_title("Grid-Connected Real-Time LP Optimization (Slide 343)", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Power [kW]")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(loc="upper left", ncol=3, fontsize=8)

    # Subplot 3: Battery State of Charge (SoC) Tracking
    axes[2].plot(time_h, df_rbc["soc_pct"], label="SoC: RBC (Off-Grid)", color="teal", linestyle="-", linewidth=2)
    axes[2].plot(time_h, df_lp_off["soc_pct"], label="SoC: LP (Off-Grid)", color="purple", linestyle="--", linewidth=2)
    axes[2].plot(time_h, df_lp_grid["soc_pct"], label="SoC: LP (Grid-Tied)", color="blue", linestyle=":", linewidth=2)
    axes[2].axhline(soc_min / bat_capacity_kwh * 100, color="r", linestyle="--", alpha=0.5, label="Min SoC (20%)")
    axes[2].axhline(soc_max / bat_capacity_kwh * 100, color="g", linestyle="--", alpha=0.5, label="Max SoC (95%)")
    axes[2].set_title("Battery State of Charge Trajectory (Slide 304)", fontsize=11, fontweight="bold")
    axes[2].set_xlabel("Time of Day [hours]")
    axes[2].set_ylabel("SoC [%]")
    axes[2].set_xlim(0, 24)
    axes[2].set_ylim(10, 100)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(loc="upper right", ncol=3, fontsize=8)

    plt.tight_layout()
    plot_path = "examples/opt_2_real_time_comparison.png"
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"\nFigure saved successfully to: {plot_path}")


if __name__ == "__main__":
    verify_slide_213_test_points()
    run_day_simulation()
