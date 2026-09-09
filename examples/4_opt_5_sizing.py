"""
4_opt_5_sizing.py
=================
Optimal microgrid sizing and long-term investment planning.
Course: ELEN0445 - Microgrids, Université de Liège.
Slide deck: opt_5_sizing

Illustrates:
1. Multi-year investment problem over 20-year lifetime (Slides 249-289).
2. Representative days operational aggregation (Slides 493, 624).
3. Linking sizing variables (PV, Battery, Inverter, Genset, Grid) to operational dispatch.
4. Net Present Value (NPV) calculation with discount rate d.
5. Sensitivity scenarios matching the lecture case study (Slides 515-600):
   - Base Case: Off-Grid (zero grid connection)
   - Scenario A: Export tariff 0.10 EUR/kWh
   - Scenario B: Export tariff 0.20 EUR/kWh
   - Scenario C: Discount rate 5% (d = 0.05)
   - Scenario D: Fuel price increase (+0.10 EUR/kWh)
6. Summary table and sensitivity visualizations.
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


def annuity_factor(discount_rate: float, years: int = 20) -> float:
    """Computes the present value factor for constant annual cash flows."""
    if np.isclose(discount_rate, 0.0):
        return float(years)
    return float((1.0 - (1.0 + discount_rate) ** (-years)) / discount_rate)


class MicrogridSizingModel:
    """
    Formulates and solves the joint investment and multi-period operational sizing LP.
    """

    def __init__(
        self,
        investment_horizon_years: int = 20,
        discount_rate: float = 0.0,
        # Unit CAPEX parameters (aligned with course parameters.py)
        capex_pv_eur_kw: float = 400.0,      # 0.40 EUR/Wp
        capex_bat_eur_kwh: float = 370.0,    # ~400 EUR / 1.08 kWh unit
        capex_inv_eur_kw: float = 250.0,     # Inverter unit price
        capex_gen_eur_kw: float = 200.0,     # Genset cost per kW
        capex_grid_eur_kw: float = 150.0,    # Grid subscription connection fee
        # Unit OPEX parameters
        fuel_cost_eur_kwh: float = 0.35,     # Genset fuel cost
        grid_import_eur_kwh: float = 0.28,   # Grid import price
        grid_export_eur_kwh: float = 0.00,   # Grid export feed-in tariff
        bat_deg_eur_kwh: float = 0.01,       # Battery throughput fee
        # Technical parameters
        eta_charge: float = 0.95,
        eta_discharge: float = 0.95,
        soc_min_ratio: float = 0.20,
        soc_max_ratio: float = 0.90,
        soc_init_ratio: float = 0.50,
        allow_grid: bool = True,
        max_pv_kw: float = 25.0,
        max_bat_kwh: float = 60.0,
        max_gen_kw: float = 20.0,
        max_grid_kw: float = 25.0,
    ):
        self.years = investment_horizon_years
        self.d = discount_rate
        self.af = annuity_factor(discount_rate, investment_horizon_years)

        self.pi_c_pv   = capex_pv_eur_kw
        self.pi_c_bat  = capex_bat_eur_kwh
        self.pi_c_inv  = capex_inv_eur_kw
        self.pi_c_gen  = capex_gen_eur_kw
        self.pi_c_grid = capex_grid_eur_kw

        self.pi_fuel = fuel_cost_eur_kwh
        self.pi_imp  = grid_import_eur_kwh
        self.pi_exp  = grid_export_eur_kwh
        self.pi_deg  = bat_deg_eur_kwh

        self.eta_c = eta_charge
        self.eta_d = eta_discharge
        self.soc_min_r = soc_min_ratio
        self.soc_max_r = soc_max_ratio
        self.soc_init_r = soc_init_ratio

        self.allow_grid = allow_grid
        self.max_pv = max_pv_kw
        self.max_bat = max_bat_kwh
        self.max_gen = max_gen_kw
        self.max_grid = max_grid_kw if allow_grid else 0.0

    def solve(self, rep_days_data: dict) -> dict:
        """
        Builds and solves the sizing LP over the representative operating days.
        """
        days = rep_days_data["days"]
        weights = rep_days_data["weights"]
        day_keys = list(days.keys())
        n_days = len(day_keys)
        n_steps = rep_days_data["steps_per_day"]
        dt = rep_days_data["resolution_min"] / 60.0

        # Sizing variables (5 variables):
        # 0: C_pv       [kWp]
        # 1: C_bat      [kWh]
        # 2: P_inv      [kW]
        # 3: P_gen_max  [kW]
        # 4: P_grid_max [kW]
        n_sizing = 5

        # Per-day operational variables (7 * n_steps):
        # For each day d and step t in 0..n_steps-1:
        #   p_pv[d, t]
        #   p_c[d, t]
        #   p_d[d, t]
        #   p_gen[d, t]
        #   p_imp[d, t]
        #   p_exp[d, t]
        #   s[d, t]
        # Total variables: 5 + n_days * 7 * n_steps
        vars_per_day = 7 * n_steps
        total_vars = n_sizing + n_days * vars_per_day

        def day_offset(d_idx):
            return n_sizing + d_idx * vars_per_day

        # Objective vector c:
        # CAPEX terms + Annuity * Yearly OPEX
        c = np.zeros(total_vars)
        c[0] = self.pi_c_pv
        c[1] = self.pi_c_bat
        c[2] = self.pi_c_inv
        c[3] = self.pi_c_gen
        c[4] = self.pi_c_grid

        for d_idx, k in enumerate(day_keys):
            w_d = weights[k]
            base = day_offset(d_idx)
            for t in range(n_steps):
                # Annual weighting factor for cash flow: annuity_factor * (weight_days * dt)
                factor = self.af * w_d * dt
                c[base + 0 * n_steps + t] = 0.0                      # p_pv has zero fuel cost
                c[base + 1 * n_steps + t] = factor * self.pi_deg     # p_c degradation
                c[base + 2 * n_steps + t] = factor * self.pi_deg     # p_d degradation
                c[base + 3 * n_steps + t] = factor * self.pi_fuel    # p_gen fuel
                c[base + 4 * n_steps + t] = factor * self.pi_imp     # p_imp electricity tariff
                c[base + 5 * n_steps + t] = -factor * self.pi_exp    # p_exp feed-in revenue
                c[base + 6 * n_steps + t] = 0.0                      # s[d, t]

        eq_rows, b_eq_list = [], []
        ub_rows, b_ub_list = [], []

        for d_idx, k in enumerate(day_keys):
            d_pv_norm = days[k]["pv"]   # Normalized PV profile [kW / kWp]
            d_load = days[k]["load"]    # Demand profile [kW]
            base = day_offset(d_idx)

            for t in range(n_steps):
                # 1. Power Balance: p_pv + p_d + p_gen + p_imp - p_c - p_exp = load[t]
                row_bal = np.zeros(total_vars)
                row_bal[base + 0 * n_steps + t] = 1.0  # p_pv
                row_bal[base + 2 * n_steps + t] = 1.0  # p_d
                row_bal[base + 3 * n_steps + t] = 1.0  # p_gen
                row_bal[base + 4 * n_steps + t] = 1.0  # p_imp
                row_bal[base + 1 * n_steps + t] = -1.0 # -p_c
                row_bal[base + 5 * n_steps + t] = -1.0 # -p_exp
                eq_rows.append(row_bal)
                b_eq_list.append(d_load[t])

                # 2. Battery Storage Dynamics:
                # s[t+1] - s[t] - eta_c * dt * p_c[t] + (dt / eta_d) * p_d[t] = 0
                # Cyclical boundary: s[n_steps] wraps around to s[0]!
                t_next = (t + 1) % n_steps
                row_soc = np.zeros(total_vars)
                row_soc[base + 6 * n_steps + t_next] = 1.0
                row_soc[base + 6 * n_steps + t]      = -1.0
                row_soc[base + 1 * n_steps + t]      = -self.eta_c * dt
                row_soc[base + 2 * n_steps + t]      = dt / self.eta_d
                eq_rows.append(row_soc)
                b_eq_list.append(0.0)

                # 3. Capacity Linking Inequalities:
                # - PV production <= Normalized_profile * C_pv
                #   p_pv[d, t] - d_pv_norm[t] * C_pv <= 0
                row_pv = np.zeros(total_vars)
                row_pv[base + 0 * n_steps + t] = 1.0
                row_pv[0] = -d_pv_norm[t]
                ub_rows.append(row_pv)
                b_ub_list.append(0.0)

                # - Battery power <= P_inv:
                #   p_c[d, t] - P_inv <= 0
                #   p_d[d, t] - P_inv <= 0
                row_inv_c = np.zeros(total_vars)
                row_inv_c[base + 1 * n_steps + t] = 1.0
                row_inv_c[2] = -1.0
                ub_rows.append(row_inv_c)
                b_ub_list.append(0.0)

                row_inv_d = np.zeros(total_vars)
                row_inv_d[base + 2 * n_steps + t] = 1.0
                row_inv_d[2] = -1.0
                ub_rows.append(row_inv_d)
                b_ub_list.append(0.0)

                # - Generator power <= P_gen_max
                #   p_gen[d, t] - P_gen_max <= 0
                row_gen = np.zeros(total_vars)
                row_gen[base + 3 * n_steps + t] = 1.0
                row_gen[3] = -1.0
                ub_rows.append(row_gen)
                b_ub_list.append(0.0)

                # - Grid import & export <= P_grid_max
                row_g_imp = np.zeros(total_vars)
                row_g_imp[base + 4 * n_steps + t] = 1.0
                row_g_imp[4] = -1.0
                ub_rows.append(row_g_imp)
                b_ub_list.append(0.0)

                row_g_exp = np.zeros(total_vars)
                row_g_exp[base + 5 * n_steps + t] = 1.0
                row_g_exp[4] = -1.0
                ub_rows.append(row_g_exp)
                b_ub_list.append(0.0)

                # - Storage SoC limits:
                #   s[d, t] - soc_max_ratio * C_bat <= 0
                #   -s[d, t] + soc_min_ratio * C_bat <= 0
                row_soc_max = np.zeros(total_vars)
                row_soc_max[base + 6 * n_steps + t] = 1.0
                row_soc_max[1] = -self.soc_max_r
                ub_rows.append(row_soc_max)
                b_ub_list.append(0.0)

                row_soc_min = np.zeros(total_vars)
                row_soc_min[base + 6 * n_steps + t] = -1.0
                row_soc_min[1] = self.soc_min_r
                ub_rows.append(row_soc_min)
                b_ub_list.append(0.0)

        A_eq = np.array(eq_rows)
        b_eq = np.array(b_eq_list)
        A_ub = np.array(ub_rows)
        b_ub = np.array(b_ub_list)

        # Bounds on variables
        bounds = [(0.0, None)] * total_vars
        bounds[0] = (0.0, self.max_pv)
        bounds[1] = (0.0, self.max_bat)
        bounds[2] = (0.0, self.max_pv + self.max_gen) # Inverter power bound
        bounds[3] = (0.0, self.max_gen)
        bounds[4] = (0.0, self.max_grid)

        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if not res.success:
            raise RuntimeError(f"Sizing LP failed: {res.message}")

        x = res.x
        c_pv_opt   = x[0]
        c_bat_opt  = x[1]
        p_inv_opt  = x[2]
        p_gen_opt  = x[3]
        p_grid_opt = x[4]

        # Calculate CAPEX and annual OPEX
        capex = (
            self.pi_c_pv * c_pv_opt
            + self.pi_c_bat * c_bat_opt
            + self.pi_c_inv * p_inv_opt
            + self.pi_c_gen * p_gen_opt
            + self.pi_c_grid * p_grid_opt
        )

        annual_opex = 0.0
        for d_idx, k in enumerate(day_keys):
            w_d = weights[k]
            base = day_offset(d_idx)
            gen_energy = (x[base + 3 * n_steps : base + 4 * n_steps] * dt).sum()
            imp_energy = (x[base + 4 * n_steps : base + 5 * n_steps] * dt).sum()
            exp_energy = (x[base + 5 * n_steps : base + 6 * n_steps] * dt).sum()
            bat_energy = ((x[base + 1 * n_steps : base + 2 * n_steps] + x[base + 2 * n_steps : base + 3 * n_steps]) * dt).sum()

            day_opex = (
                self.pi_fuel * gen_energy
                + self.pi_imp * imp_energy
                - self.pi_exp * exp_energy
                + self.pi_deg * bat_energy
            )
            annual_opex += w_d * day_opex

        total_lifetime_cost = capex + self.af * annual_opex
        npv = -total_lifetime_cost

        # Extract representative day profiles
        rep_results = {}
        for d_idx, k in enumerate(day_keys):
            base = day_offset(d_idx)
            rep_results[k] = {
                "p_pv":  x[base + 0 * n_steps : base + 1 * n_steps],
                "p_c":   x[base + 1 * n_steps : base + 2 * n_steps],
                "p_d":   x[base + 2 * n_steps : base + 3 * n_steps],
                "p_gen": x[base + 3 * n_steps : base + 4 * n_steps],
                "p_imp": x[base + 4 * n_steps : base + 5 * n_steps],
                "p_exp": x[base + 5 * n_steps : base + 6 * n_steps],
                "soc":   x[base + 6 * n_steps : base + 7 * n_steps],
            }

        return {
            "c_pv": c_pv_opt,
            "c_bat": c_bat_opt,
            "p_inv": p_inv_opt,
            "p_gen": p_gen_opt,
            "p_grid": p_grid_opt,
            "capex": capex,
            "annual_opex": annual_opex,
            "lifetime_cost": total_lifetime_cost,
            "npv": npv,
            "annuity_factor": self.af,
            "rep_results": rep_results,
        }


# =============================================================================
# Run Sizing Scenarios - Matching Slides 515-600
# =============================================================================

def run_sizing_study():
    print("\n" + "=" * 75)
    print("MICROGRID OPTIMAL SIZING & INVESTMENT STUDY (Slides 515-600)")
    print("=" * 75)

    rep_data = common_data.generate_representative_days(resolution_min=15)

    scenarios = [
        ("Base Case (Off-Grid, d=0.0)", MicrogridSizingModel(allow_grid=False, discount_rate=0.0)),
        ("Scenario A (Export tariff 0.10 EUR/kWh)", MicrogridSizingModel(allow_grid=True, grid_export_eur_kwh=0.10, discount_rate=0.0)),
        ("Scenario B (Export tariff 0.20 EUR/kWh)", MicrogridSizingModel(allow_grid=True, grid_export_eur_kwh=0.20, discount_rate=0.0)),
        ("Scenario C (Discount rate d = 0.05)", MicrogridSizingModel(allow_grid=False, discount_rate=0.05)),
        ("Scenario D (Fuel price +0.10 EUR/kWh)", MicrogridSizingModel(allow_grid=False, fuel_cost_eur_kwh=0.45, discount_rate=0.0)),
    ]

    results_table = []
    scenario_outputs = []

    for name, model in scenarios:
        res = model.solve(rep_data)
        scenario_outputs.append((name, model, res))

        results_table.append({
            "Scenario": name,
            "NPV (EUR)": f"{res['npv']:.1f}",
            "CAPEX (EUR)": f"{res['capex']:.1f}",
            "Yearly OPEX (EUR)": f"{res['annual_opex']:.1f}",
            "PV (kWp)": f"{max(0.0, res['c_pv']):.2f}",
            "Storage (kWh)": f"{max(0.0, res['c_bat']):.2f}",
            "Inverter (kW)": f"{max(0.0, res['p_inv']):.2f}",
            "Genset (kW)": f"{max(0.0, res['p_gen']):.2f}",
            "Grid (kW)": f"{max(0.0, res['p_grid']):.2f}",
        })

    df_report = pd.DataFrame(results_table)
    print(df_report.to_string(index=False))

    # =========================================================================
    # Visualizations
    # =========================================================================
    fig = plt.figure(figsize=(15, 11))

    # Subplot 1: Sized Asset Capacities Across Scenarios
    ax1 = plt.subplot2grid((2, 2), (0, 0))
    scen_labels = ["Base (Off-grid)", "Export 0.10", "Export 0.20", "Discount 5%", "Fuel +0.10"]
    x_pos = np.arange(len(scen_labels))
    w = 0.18

    pv_vals  = [s[2]["c_pv"] for s in scenario_outputs]
    bat_vals = [s[2]["c_bat"] for s in scenario_outputs]
    inv_vals = [s[2]["p_inv"] for s in scenario_outputs]
    gen_vals = [s[2]["p_gen"] for s in scenario_outputs]

    ax1.bar(x_pos - 1.5 * w, pv_vals, width=w, color="gold", edgecolor="black", label="PV [kWp]")
    ax1.bar(x_pos - 0.5 * w, bat_vals, width=w, color="teal", edgecolor="black", label="Battery [kWh]")
    ax1.bar(x_pos + 0.5 * w, inv_vals, width=w, color="orange", edgecolor="black", label="Inverter [kW]")
    ax1.bar(x_pos + 1.5 * w, gen_vals, width=w, color="firebrick", edgecolor="black", label="Genset [kW]")

    ax1.set_title("Optimal Asset Capacities by Scenario (Slide 515-600)", fontsize=11, fontweight="bold")
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(scen_labels, rotation=15)
    ax1.set_ylabel("Capacity [kW or kWh]")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper right", fontsize=8)

    # Subplot 2: CAPEX vs Lifetime OPEX vs NPV
    ax2 = plt.subplot2grid((2, 2), (0, 1))
    capex_vals = [s[2]["capex"] for s in scenario_outputs]
    opex_lifetime = [s[2]["annuity_factor"] * s[2]["annual_opex"] for s in scenario_outputs]

    ax2.bar(x_pos - 0.2, capex_vals, width=0.35, color="navy", label="Initial CAPEX")
    ax2.bar(x_pos + 0.2, opex_lifetime, width=0.35, color="crimson", label="20-Yr Discounted OPEX")
    ax2.set_title("Financial Breakdown (CAPEX vs. 20-Year OPEX)", fontsize=11, fontweight="bold")
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(scen_labels, rotation=15)
    ax2.set_ylabel("Cost [EUR]")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper right", fontsize=8)

    # Subplots 3 & 4: Optimal Operational Dispatch on 2 Representative Days (Base Case)
    base_res = scenario_outputs[0][2]
    time_h = rep_data["time_hours"]

    # Representative Day: Summer Sunny
    ax3 = plt.subplot2grid((2, 2), (1, 0))
    d_sum = base_res["rep_results"]["summer_sunny"]
    sum_load = rep_data["days"]["summer_sunny"]["load"]
    ax3.plot(time_h, sum_load, "k--", label="Load", linewidth=1.5)
    ax3.step(time_h, d_sum["p_pv"], color="orange", label="PV", where="mid")
    ax3.step(time_h, d_sum["p_d"] - d_sum["p_c"], color="teal", label="Battery", where="mid")
    ax3.step(time_h, d_sum["p_gen"], color="firebrick", label="Genset", where="mid")
    ax3.set_title("Base Case Dispatch: Representative Summer Sunny Day", fontsize=10, fontweight="bold")
    ax3.set_xlabel("Hour of Day")
    ax3.set_ylabel("Power [kW]")
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc="upper left", fontsize=8)

    # Representative Day: Winter Cloudy
    ax4 = plt.subplot2grid((2, 2), (1, 1))
    d_win = base_res["rep_results"]["winter_cloudy"]
    win_load = rep_data["days"]["winter_cloudy"]["load"]
    ax4.plot(time_h, win_load, "k--", label="Load", linewidth=1.5)
    ax4.step(time_h, d_win["p_pv"], color="orange", label="PV", where="mid")
    ax4.step(time_h, d_win["p_d"] - d_win["p_c"], color="teal", label="Battery", where="mid")
    ax4.step(time_h, d_win["p_gen"], color="firebrick", label="Genset", where="mid")
    ax4.set_title("Base Case Dispatch: Representative Winter Cloudy Day", fontsize=10, fontweight="bold")
    ax4.set_xlabel("Hour of Day")
    ax4.set_ylabel("Power [kW]")
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc="upper left", fontsize=8)

    plt.tight_layout()
    plot_path = "examples/opt_5_sizing_sensitivities.png"
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"\nFigure saved successfully to: {plot_path}")


if __name__ == "__main__":
    run_sizing_study()
