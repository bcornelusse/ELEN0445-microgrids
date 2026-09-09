# ELEN0445 Microgrids

This microgrids course is given at the Master's level at the Université de Liège (ULiège).
The goal of this course is to be applied and practical, with lab visits, simulation, and sizing of installations.

### Prerequisites:
- Notions of electrical circuits analysis ([Livre Circuits Électriques ELEC0053](https://github.com/bcornelusse/livre_circuits_electriques_ELEC0053/))
- Notions of optimization / mathematical programming
- Notions of scientific computing (we will use Python)

**Instructor:** Bertrand Cornélusse  
**Teaching assistants:** Thomas Stegen, Clément Moureau

---

# Course Schedule (2025–2026)

| Date | Lecture | Topic | Materials & Code |
| :--- | :---: | :--- | :--- |
| | | **Module 1: Microgrid Architecture & Components** | |
| February 5 | 1 | Introduction | [Slides](slides/1_intro_and_organization/1_intro_and_organization.pdf) |
| | | Generation devices and power electronics interfaces | [Slides](slides/2_power_sources_and_interfaces/2_power_sources_and_interfaces.pdf) |
| | | Energy storage | [Slides](slides/3_storage/3_storage.pdf) |
| | | Microgrid architectures | [Slides](slides/4_architectures/4_architectures.pdf) |
| February 12 | 2 | Assignment 1: Lab microgrid visit and description | Submit on eCampus (Deadline: Feb 19) |
| | | Hands-on session: Design a PV + storage installation | SMA Sunny Explorer tool |
| February 19 | 3 | Assignment 2: Visit of AIM and design of their PV + storage installation | |
| February 27 | | Deadline for assignment 2 | |
| March 5 | 4 | Discussion and feedback on assignment 2 with a professional company | |
| | | **Module 2: Inverter & Microgrid Control** | |
| March 12 | 5 | Inverter control (VSC, GFOR/GFOL, dq0 frame, PLL) | [Slides](slides/5_inverter_control/5_inverter_control.pdf) |
| March 19 | 6 | Assignment 3 statement: Real-time control of the lab microgrid in Typhoon-HIL | See eCampus |
| | | **Module 3: Microgrid Optimization & Forecasting** | |
| March 26 | 8 | Introduction to the optimization module | [Slides](slides/opt_1_intro/opt_1_intro.pdf) |
| | | Introduction to optimization: a simple network flow problem | [Densys Slides](https://github.com/bcornelusse/DENSYS-school/blob/main/Lectures/densys_1-2-LP_network-flow/densys_1-2-LP_network-flow.pdf) |
| | | Linear programming notebooks | [Colab Example 1](https://colab.research.google.com/drive/1xgO3EhGoG6P5E9BVV7QyPgLJM5HdNDrY?usp=sharing), [Colab Example 2](https://colab.research.google.com/drive/1ujoTNfu2_sCoVK7ksqbXgusmAAizvIip?usp=sharing) |
| | | Hands-on session | [Colab Hands-on](https://colab.research.google.com/drive/1lrWL7sOrazTzlapVxcxrv_ZvVUZADC0h?usp=sharing) |
| | | Real-time optimization of a microgrid | [Slides](slides/opt_2_RT/opt_2_RT.pdf) · [Python Code](examples/1_opt_2_real_time.py) |
| April 2 | 9 | Work session on assignment 3 | |
| April 9 | 10 | Introduction to machine learning | [Densys ML Slides](https://github.com/bcornelusse/DENSYS-school/blob/main/Lectures/densys_ML/densys-ML.pdf) |
| | | Introduction to point and probabilistic forecasting | [Slides](slides/opt_3_forecasting/opt_3_forecasting.pdf) · [Python Code](examples/2_opt_3_forecasting.py) |
| | | Hands-on forecasting session | [Colab Session](https://colab.research.google.com/drive/1hvI10_m99pxUdT3mnqaDrtBieKiPjTwf?usp=sharing) |
| April 16 | 11 | Operational planning & Receding Horizon MPC | [Slides](slides/opt_4_planning/opt_4_planning.pdf) · [Python Code](examples/3_opt_4_planning.py) |
| | | Optimal sizing of microgrid assets | [Slides](slides/opt_5_sizing/opt_5_sizing.pdf) · [Python Code](examples/4_opt_5_sizing.py) |
| | | Presentation of assignment 3 | See schedule |
| | | Assignment 4 statement (Operational planning & sizing) | [Description](Homeworks/OPSizing/µG_Pres_HW4_1.pdf) · [Files](Homeworks/OPSizing/HW4_1.zip) |
| May 7 | 12 | Q&A session on assignment 4 | |

---

## 💻 Python Optimization & Forecasting Examples

The [`examples/`](examples/) folder provides standalone, self-contained Python scripts that illustrate the mathematical formulations and economic trade-offs from lectures `opt_2` through `opt_5`. All scripts run with synthetic data and use the open-source **HiGHS** solver included in SciPy (no commercial solver license required).

1. **[Real-Time Control (`1_opt_2_real_time.py`)](examples/1_opt_2_real_time.py)**:
   - Rule-Based Controller (RBC, Slide 151) vs. Linear Programming (LP Problem 1 & 2 with slacks, Slides 224, 269).
   - Infeasibility handling on capacity overload.
   - Battery SoC tracking with separate charge/discharge efficiencies (Slide 304) and grid-connected dispatch (Slide 343).

2. **[Forecasting & Metrics (`2_opt_3_forecasting.py`)](examples/2_opt_3_forecasting.py)**:
   - Baseline naive persistence (Slide 393), seasonal persistence (24h lag), and autoregressive ML regression.
   - Multi-step evaluation ($k \in [1, 24]$h) computing bias, MAE, RMSE, NMAE, and NRMSE (Slide 616).
   - Probabilistic quantile regression via Pinball Loss LP ($\tau \in \{0.10, 0.50, 0.90\}$) with calibration and sharpness checks.

3. **[Operational Planning & MPC (`3_opt_4_planning.py`)](examples/3_opt_4_planning.py)**:
   - 24-hour day-ahead multi-period scheduling with Time-of-Use (TOU) tariff arbitrage.
   - Peak shaving capacity constraints and penalties (Slide 268).
   - Demand-side management (DSM) for flexible shiftable appliances (Slide 364).
   - Day-ahead Open-Loop plan vs. Closed-Loop Receding Horizon MPC under forecast error (Slide 147).

4. **[Optimal Sizing & Investment (`4_opt_5_sizing.py`)](examples/4_opt_5_sizing.py)**:
   - 20-year investment sizing LP optimizing PV, Battery capacity, Inverter power, Genset, and Grid connection.
   - Net Present Value (NPV) calculation over representative seasonal operating days (Slide 493, 624).
   - Case study sensitivities matching lecture slides 515–600 (off-grid base case, export feed-in tariffs, discount rate 5%, fuel price increase).

### Quick Setup & Execution

```bash
# Set up environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r examples/requirements.txt

# Run any simulation
python examples/1_opt_2_real_time.py
python examples/2_opt_3_forecasting.py
python examples/3_opt_4_planning.py
python examples/4_opt_5_sizing.py
```

For more details on mathematical formulations and instructions on plugging in real CSV measurement data, see the [Examples Documentation](examples/README.md).
