"""
3_opt_4_planning.py
===================
Operational planning and receding horizon (MPC) optimization in microgrids.
Course: ELEN0445 - Microgrids, Université de Liège.
Slide deck: opt_4_planning

Illustrates:
1. Multi-period day-ahead scheduling (LP formulation over 24h).
2. Time-of-Use (TOU) tariff arbitrage and battery degradation penalty.
3. Peak shaving / monthly peak capacity constraint (Slide 268).
4. Demand-Side Management (DSM): Flexible shiftable load scheduling (Slides 364-426).
5. Open-Loop vs. Receding Horizon (MPC) under forecast errors (Slides 147-175).
6. Performance comparison and dispatch visualization.
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


class DayAheadPlanner:
    """
    Formulates and solves the multi-period day-ahead microgrid operational planning problem.
    """

    def __init__(
        self,
        n_steps: int = 96,
        dt_hours: float = 0.25,
        bat_capacity_kwh: float = 14.0,
        soc_min_pct: float = 0.20,
        soc_max_pct: float = 0.90,
        soc_init_pct: float = 0.50,
        p_bat_max_kw: float = 5.0,
        eta_charge: float = 0.95,
        eta_discharge: float = 0.95,
        bat_deg_cost: float = 0.01, # EUR/kWh throughput
        p_grid_import_max: float = 10.0,
        p_grid_export_max: float = 10.0,
        peak_tariff_eur_kw: float = 5.0, # Capacity peak penalty [EUR/kW]
    ):
        self.N = n_steps
        self.dt = dt_hours
        self.C_bat = bat_capacity_kwh
        self.s_min = soc_min_pct * bat_capacity_kwh
        self.s_max = soc_max_pct * bat_capacity_kwh
        self.s_init = soc_init_pct * bat_capacity_kwh
        self.p_bat_max = p_bat_max_kw
        self.eta_c = eta_charge
        self.eta_d = eta_discharge
        self.pi_deg = bat_deg_cost
        self.p_imp_max = p_grid_import_max
        self.p_exp_max = p_grid_export_max
        self.pi_peak = peak_tariff_eur_kw

    def solve(
        self,
        p_load: np.ndarray,
        p_pv_max: np.ndarray,
        pi_imp: np.ndarray,
        pi_exp: np.ndarray,
        flex_load_config: dict | None = None,
        s_current: float | None = None,
        include_peak_shaving: bool = True,
    ) -> dict:
        """
        Decision variables index:
          - p_imp[t]:        0 <= t < N           (N vars)
          - p_exp[t]:        N <= t < 2N          (N vars)
          - p_c[t]:          2N <= t < 3N         (N vars)
          - p_d[t]:          3N <= t < 4N         (N vars)
          - p_pv[t]:         4N <= t < 5N         (N vars)
          - s[t]:            5N <= t < 6N + 1     (N + 1 vars: s_0, ..., s_N)
          - p_flex[t]:       6N+1 <= t < 7N + 1   (N vars)
          - P_peak:          7N + 1               (1 var)
        Total vars: 7N + 2
        """
        N = len(p_load)
        dt = self.dt
        s_0 = self.s_init if s_current is None else s_current

        # Variable offsets
        idx_imp = 0
        idx_exp = N
        idx_c   = 2 * N
        idx_d   = 3 * N
        idx_pv  = 4 * N
        idx_s   = 5 * N
        idx_flx = 6 * N + 1
        idx_pk  = 7 * N + 1
        n_vars  = 7 * N + 2

        # 1. Objective function
        c = np.zeros(n_vars)
        for t in range(N):
            c[idx_imp + t] = pi_imp[t] * dt
            c[idx_exp + t] = -pi_exp[t] * dt
            c[idx_c + t]   = self.pi_deg * dt
            c[idx_d + t]   = self.pi_deg * dt
            # p_pv has 0 marginal cost
            # s has 0 direct cost

        if include_peak_shaving:
            c[idx_pk] = self.pi_peak

        # 2. Equality constraints
        # - Power balance for t in 0..N-1:
        #   p_imp[t] - p_exp[t] - p_c[t] + p_d[t] + p_pv[t] - p_flex[t] = p_load[t]
        # - Battery SoC dynamics for t in 0..N-1:
        #   s[t+1] - s[t] - eta_c * dt * p_c[t] + (dt / eta_d) * p_d[t] = 0
        # - Initial SoC: s[0] = s_0
        # - Flexible load total energy requirement (if configured)
        eq_rows = []
        b_eq_list = []

        # Initial condition: s[0] = s_0
        row_s0 = np.zeros(n_vars)
        row_s0[idx_s] = 1.0
        eq_rows.append(row_s0)
        b_eq_list.append(s_0)

        # Balances and dynamics
        for t in range(N):
            # Power balance
            row_bal = np.zeros(n_vars)
            row_bal[idx_imp + t] = 1.0
            row_bal[idx_exp + t] = -1.0
            row_bal[idx_c + t]   = -1.0
            row_bal[idx_d + t]   = 1.0
            row_bal[idx_pv + t]  = 1.0
            row_bal[idx_flx + t] = -1.0
            eq_rows.append(row_bal)
            b_eq_list.append(p_load[t])

            # SoC state equation: s[t+1] - s[t] - eta_c*dt*p_c + dt/eta_d*p_d = 0
            row_soc = np.zeros(n_vars)
            row_soc[idx_s + t + 1] = 1.0
            row_soc[idx_s + t]     = -1.0
            row_soc[idx_c + t]     = -self.eta_c * dt
            row_soc[idx_d + t]     = dt / self.eta_d
            eq_rows.append(row_soc)
            b_eq_list.append(0.0)

        # Flexible load energy requirement
        if flex_load_config is not None:
            e_req = flex_load_config["energy_req_kwh"]
            t_st  = flex_load_config["t_start_step"]
            t_en  = flex_load_config["t_end_step"]
            row_flx = np.zeros(n_vars)
            for t in range(t_st, t_en + 1):
                if t < N:
                    row_flx[idx_flx + t] = dt
            eq_rows.append(row_flx)
            b_eq_list.append(e_req)

        A_eq = np.array(eq_rows)
        b_eq = np.array(b_eq_list)

        # 3. Inequality constraints
        # - Peak shaving: p_imp[t] - P_peak <= 0
        # - Terminal SoC: s[N] >= s_0 (represented as -s[N] <= -s_0)
        ub_rows = []
        b_ub_list = []

        if include_peak_shaving:
            for t in range(N):
                row_pk = np.zeros(n_vars)
                row_pk[idx_imp + t] = 1.0
                row_pk[idx_pk]      = -1.0
                ub_rows.append(row_pk)
                b_ub_list.append(0.0)

        # Terminal state constraint (do not deplete battery at end of horizon): s[N] >= s_0
        row_term = np.zeros(n_vars)
        row_term[idx_s + N] = -1.0
        ub_rows.append(row_term)
        b_ub_list.append(-s_0)

        A_ub = np.array(ub_rows) if ub_rows else None
        b_ub = np.array(b_ub_list) if b_ub_list else None

        # 4. Bounds
        bounds = [(0.0, None)] * n_vars

        for t in range(N):
            bounds[idx_imp + t] = (0.0, self.p_imp_max)
            bounds[idx_exp + t] = (0.0, self.p_exp_max)
            bounds[idx_c + t]   = (0.0, self.p_bat_max)
            bounds[idx_d + t]   = (0.0, self.p_bat_max)
            bounds[idx_pv + t]  = (0.0, p_pv_max[t])
            bounds[idx_s + t]   = (self.s_min, self.s_max)

            # Flexible load bounds
            if flex_load_config is not None:
                t_st = flex_load_config["t_start_step"]
                t_en = flex_load_config["t_end_step"]
                p_max = flex_load_config["p_max_kw"]
                if t_st <= t <= t_en:
                    bounds[idx_flx + t] = (0.0, p_max)
                else:
                    bounds[idx_flx + t] = (0.0, 0.0)
            else:
                bounds[idx_flx + t] = (0.0, 0.0)

        bounds[idx_s + N] = (self.s_min, self.s_max)
        bounds[idx_pk]    = (0.0, self.p_imp_max)

        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if not res.success:
            raise RuntimeError(f"Day-ahead planning LP failed: {res.message}")

        x = res.x
        return {
            "p_imp": x[idx_imp : idx_imp + N],
            "p_exp": x[idx_exp : idx_exp + N],
            "p_c":   x[idx_c : idx_c + N],
            "p_d":   x[idx_d : idx_d + N],
            "p_pv":  x[idx_pv : idx_pv + N],
            "p_bat": x[idx_d : idx_d + N] - x[idx_c : idx_c + N], # positive = discharging
            "soc":   x[idx_s : idx_s + N + 1],
            "p_flex": x[idx_flx : idx_flx + N],
            "p_peak": x[idx_pk],
            "cost":  res.fun,
        }


# =============================================================================
# Receding Horizon (MPC) Simulation - Slides 147-175
# =============================================================================

def run_receding_horizon_simulation():
    print("\n" + "=" * 70)
    print("OPERATIONAL PLANNING & RECEDING HORIZON (MPC) SIMULATION")
    print("=" * 70)

    res_min = 15
    dt_hours = res_min / 60.0
    n_steps = int(24 * 60 / res_min) # 96

    # 1. Ground truth actual profiles for day
    df_pv_true = common_data.generate_synthetic_pv(n_days=1, resolution_min=res_min, peak_kw=9.0, cloudiness=0.35, seed=42)
    df_load_true = common_data.generate_synthetic_load(n_days=1, resolution_min=res_min, base_kw=1.5, peak_kw=5.5, seed=123)
    df_tou = common_data.generate_tou_tariffs(n_days=1, resolution_min=res_min, off_peak_price=0.15, peak_price=0.35, export_price=0.06)

    pv_true = df_pv_true["pv_potential_kw"].values
    load_true = df_load_true["load_kw"].values
    pi_imp = df_tou["import_price"].values
    pi_exp = df_tou["export_price"].values

    # 2. Imperfect day-ahead forecast (used by open-loop plan): has amplitude & cloud timing errors
    rng = np.random.default_rng(999)
    pv_forecast = np.clip(pv_true * (0.85 + 0.3 * np.sin(np.pi * np.arange(n_steps) / n_steps)), 0, 10.0)
    load_forecast = np.clip(load_true + rng.normal(0, 0.4, n_steps), 0.5, 7.0)

    # 3. Flexible appliance configuration (EV charging 12 kWh between 10:00 and 16:00)
    flex_config = {
        "energy_req_kwh": 12.0,
        "t_start_step": int(10.0 / dt_hours), # 10:00
        "t_end_step":   int(16.0 / dt_hours), # 16:00
        "p_max_kw":     3.5,
    }

    planner = DayAheadPlanner(n_steps=n_steps, dt_hours=dt_hours)

    # =========================================================================
    # Strategy A: Baseline (Unmanaged Microgrid)
    # =========================================================================
    # No battery storage usage; PV is self-consumed, excess exported, deficit imported
    p_net_unmanaged = load_true - pv_true
    imp_unmanaged = np.maximum(0, p_net_unmanaged)
    exp_unmanaged = np.maximum(0, -p_net_unmanaged)
    cost_unmanaged = (imp_unmanaged * pi_imp * dt_hours).sum() - (exp_unmanaged * pi_exp * dt_hours).sum()
    peak_unmanaged = np.max(imp_unmanaged)

    # =========================================================================
    # Strategy B: Open-Loop Schedule (Slide 122)
    # =========================================================================
    # Optimize once day-ahead using the imperfect forecast
    plan_open_loop = planner.solve(
        p_load=load_forecast,
        p_pv_max=pv_forecast,
        pi_imp=pi_imp,
        pi_exp=pi_exp,
        flex_load_config=flex_config,
    )

    # Apply open-loop planned battery setpoints to actual real-time conditions
    soc_ol = planner.s_init
    soc_ol_hist = [soc_ol]
    imp_ol_actual = []
    exp_ol_actual = []

    for t in range(n_steps):
        p_bat_cmd = plan_open_loop["p_bat"][t] # target dispatch
        p_flx_cmd = plan_open_loop["p_flex"][t]

        # Feasibility check on battery SoC limits
        if p_bat_cmd > 0: # Discharging
            max_dis = (soc_ol - planner.s_min) * planner.eta_d / dt_hours
            p_bat_act = min(p_bat_cmd, max(0.0, max_dis))
            soc_ol -= (p_bat_act / planner.eta_d) * dt_hours
        else: # Charging
            max_ch = (planner.s_max - soc_ol) / (planner.eta_c * dt_hours)
            p_bat_act = -min(-p_bat_cmd, max(0.0, max_ch))
            soc_ol += (-p_bat_act) * planner.eta_c * dt_hours

        soc_ol = np.clip(soc_ol, planner.s_min, planner.s_max)
        soc_ol_hist.append(soc_ol)

        # Real-time power balance must be met by grid:
        # p_imp - p_exp = load_true + p_flx_cmd - pv_true - p_bat_act
        net_demand = load_true[t] + p_flx_cmd - pv_true[t] - p_bat_act
        imp_ol_actual.append(max(0.0, net_demand))
        exp_ol_actual.append(max(0.0, -net_demand))

    imp_ol_actual = np.array(imp_ol_actual)
    exp_ol_actual = np.array(exp_ol_actual)
    cost_open_loop = (imp_ol_actual * pi_imp * dt_hours).sum() - (exp_ol_actual * pi_exp * dt_hours).sum() + planner.pi_peak * np.max(imp_ol_actual)

    # =========================================================================
    # Strategy C: Receding Horizon / Closed-Loop MPC (Slides 147-175)
    # =========================================================================
    # Re-solves every 1 hour (every 4 steps) with updated state and refreshed forecast
    replan_interval = 4
    soc_mpc = planner.s_init
    soc_mpc_hist = [soc_mpc]
    p_bat_mpc_hist = []
    p_flx_mpc_hist = []
    imp_mpc_actual = []
    exp_mpc_actual = []

    current_plan = None

    for t in range(n_steps):
        # Re-plan at replan interval
        if t % replan_interval == 0:
            rem_steps = n_steps - t
            # Fresh forecast over remaining horizon with lower error
            rem_pv_fc = pv_true[t:] * (1.0 + 0.1 * np.sin(np.arange(rem_steps)))
            rem_load_fc = load_true[t:] + rng.normal(0, 0.15, rem_steps)

            # Update flexible load config for remaining horizon
            rem_flex = None
            if flex_config is not None:
                # Remaining energy to deliver
                delivered_so_far = sum(p_flx_mpc_hist) * dt_hours
                rem_energy = max(0.0, flex_config["energy_req_kwh"] - delivered_so_far)
                rem_flex = {
                    "energy_req_kwh": rem_energy,
                    "t_start_step": max(0, flex_config["t_start_step"] - t),
                    "t_end_step":   max(0, flex_config["t_end_step"] - t),
                    "p_max_kw":     flex_config["p_max_kw"],
                }

            rem_planner = DayAheadPlanner(
                n_steps=rem_steps,
                dt_hours=dt_hours,
                bat_capacity_kwh=planner.C_bat,
                soc_min_pct=planner.s_min / planner.C_bat,
                soc_max_pct=planner.s_max / planner.C_bat,
                soc_init_pct=soc_mpc / planner.C_bat,
                p_bat_max_kw=planner.p_bat_max,
                eta_charge=planner.eta_c,
                eta_discharge=planner.eta_d,
                bat_deg_cost=planner.pi_deg,
                p_grid_import_max=planner.p_imp_max,
                p_grid_export_max=planner.p_exp_max,
                peak_tariff_eur_kw=planner.pi_peak,
            )
            current_plan = rem_planner.solve(
                p_load=rem_load_fc,
                p_pv_max=rem_pv_fc,
                pi_imp=pi_imp[t:],
                pi_exp=pi_exp[t:],
                flex_load_config=rem_flex,
                s_current=soc_mpc,
            )

        # Apply first step of receding plan
        step_in_plan = t % replan_interval
        p_bat_cmd = current_plan["p_bat"][step_in_plan]
        p_flx_cmd = current_plan["p_flex"][step_in_plan]

        if p_bat_cmd > 0: # Discharging
            max_dis = (soc_mpc - planner.s_min) * planner.eta_d / dt_hours
            p_bat_act = min(p_bat_cmd, max(0.0, max_dis))
            soc_mpc -= (p_bat_act / planner.eta_d) * dt_hours
        else: # Charging
            max_ch = (planner.s_max - soc_mpc) / (planner.eta_c * dt_hours)
            p_bat_act = -min(-p_bat_cmd, max(0.0, max_ch))
            soc_mpc += (-p_bat_act) * planner.eta_c * dt_hours

        soc_mpc = np.clip(soc_mpc, planner.s_min, planner.s_max)
        soc_mpc_hist.append(soc_mpc)
        p_bat_mpc_hist.append(p_bat_act)
        p_flx_mpc_hist.append(p_flx_cmd)

        net_demand = load_true[t] + p_flx_cmd - pv_true[t] - p_bat_act
        imp_mpc_actual.append(max(0.0, net_demand))
        exp_mpc_actual.append(max(0.0, -net_demand))

    imp_mpc_actual = np.array(imp_mpc_actual)
    exp_mpc_actual = np.array(exp_mpc_actual)
    cost_mpc = (imp_mpc_actual * pi_imp * dt_hours).sum() - (exp_mpc_actual * pi_exp * dt_hours).sum() + planner.pi_peak * np.max(imp_mpc_actual)

    # Print Comparison Summary
    print("-" * 70)
    print("PLANNING STRATEGIES PERFORMANCE COMPARISON")
    print("-" * 70)
    results = [
        {
            "Strategy": "Unmanaged Baseline (No Battery)",
            "Energy Cost (EUR)": f"{(imp_unmanaged * pi_imp * dt_hours).sum() - (exp_unmanaged * pi_exp * dt_hours).sum():.2f}",
            "Peak Import (kW)": f"{peak_unmanaged:.2f}",
            "Peak Cost (EUR)": f"{planner.pi_peak * peak_unmanaged:.2f}",
            "Total Cost (EUR)": f"{cost_unmanaged + planner.pi_peak * peak_unmanaged:.2f}",
        },
        {
            "Strategy": "Day-Ahead Open-Loop (Slide 122)",
            "Energy Cost (EUR)": f"{(imp_ol_actual * pi_imp * dt_hours).sum() - (exp_ol_actual * pi_exp * dt_hours).sum():.2f}",
            "Peak Import (kW)": f"{np.max(imp_ol_actual):.2f}",
            "Peak Cost (EUR)": f"{planner.pi_peak * np.max(imp_ol_actual):.2f}",
            "Total Cost (EUR)": f"{cost_open_loop:.2f}",
        },
        {
            "Strategy": "Receding Horizon MPC (Slide 153)",
            "Energy Cost (EUR)": f"{(imp_mpc_actual * pi_imp * dt_hours).sum() - (exp_mpc_actual * pi_exp * dt_hours).sum():.2f}",
            "Peak Import (kW)": f"{np.max(imp_mpc_actual):.2f}",
            "Peak Cost (EUR)": f"{planner.pi_peak * np.max(imp_mpc_actual):.2f}",
            "Total Cost (EUR)": f"{cost_mpc:.2f}",
        },
    ]
    df_res = pd.DataFrame(results)
    print(df_res.to_string(index=False))

    # =========================================================================
    # Visualizations
    # =========================================================================
    time_h = df_pv_true["time_hours"].values

    fig, axes = plt.subplots(3, 1, figsize=(13, 11), sharex=True)

    # Subplot 1: Day-Ahead Optimized Dispatch & Flexible Load
    axes[0].plot(time_h, load_true, "k--", label="Inelastic Load", linewidth=1.5)
    axes[0].plot(time_h, load_true + np.array(p_flx_mpc_hist), "k-", label="Total Demand (incl. DSM)", linewidth=1.8)
    axes[0].plot(time_h, pv_true, "gold", label="Actual PV", linewidth=1.5)
    axes[0].step(time_h, p_bat_mpc_hist, color="teal", label="Battery (+dis / -ch)", where="mid")
    axes[0].step(time_h, imp_mpc_actual, color="blue", label="Grid Import", where="mid")
    axes[0].step(time_h, exp_mpc_actual, color="green", label="Grid Export", where="mid")
    axes[0].set_title("Receding Horizon MPC Dispatch & DSM Load Shifting (Slide 153 & 364)", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Power [kW]")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc="upper left", ncol=3, fontsize=8)

    # Subplot 2: Dynamic Tariff & Peak Shaving
    ax_twin = axes[1].twinx()
    axes[1].step(time_h, imp_unmanaged, "r--", label="Unmanaged Import", where="mid", alpha=0.6)
    axes[1].step(time_h, imp_mpc_actual, "b-", label="MPC Import (Peak Shaved)", where="mid", linewidth=1.8)
    axes[1].axhline(np.max(imp_mpc_actual), color="blue", linestyle=":", label=f"MPC Peak: {np.max(imp_mpc_actual):.1f} kW")
    axes[1].axhline(peak_unmanaged, color="red", linestyle=":", label=f"Unmanaged Peak: {peak_unmanaged:.1f} kW")
    ax_twin.step(time_h, pi_imp, "purple", linestyle="-.", label="Tariff [EUR/kWh]", where="mid", alpha=0.7)
    axes[1].set_title("Peak Shaving & TOU Tariff Arbitrage (Slide 237-268)", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Import Power [kW]")
    ax_twin.set_ylabel("Tariff [EUR/kWh]", color="purple")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(loc="upper left", fontsize=8)
    ax_twin.legend(loc="upper right", fontsize=8)

    # Subplot 3: Battery SoC Trajectories (Open-Loop vs. Closed-Loop MPC)
    t_soc = np.linspace(0, 24, n_steps + 1)
    axes[2].plot(t_soc, np.array(soc_ol_hist) / planner.C_bat * 100, "r--", label="SoC: Open-Loop Plan", linewidth=2)
    axes[2].plot(t_soc, np.array(soc_mpc_hist) / planner.C_bat * 100, "b-", label="SoC: Receding Horizon MPC", linewidth=2)
    axes[2].axhline(planner.s_min / planner.C_bat * 100, color="r", linestyle="--", alpha=0.5, label="Min SoC")
    axes[2].axhline(planner.s_max / planner.C_bat * 100, color="g", linestyle="--", alpha=0.5, label="Max SoC")
    axes[2].set_title("Storage SoC Trajectory: Open-Loop vs. Receding Horizon MPC (Slide 147)", fontsize=11, fontweight="bold")
    axes[2].set_xlabel("Time of Day [hours]")
    axes[2].set_ylabel("Battery SoC [%]")
    axes[2].set_xlim(0, 24)
    axes[2].set_ylim(15, 95)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(loc="lower left", ncol=4, fontsize=8)

    plt.tight_layout()
    plot_path = "examples/opt_4_planning_and_mpc.png"
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"\nFigure saved successfully to: {plot_path}")


if __name__ == "__main__":
    run_receding_horizon_simulation()
