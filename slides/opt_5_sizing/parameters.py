# Time
RESOLUTION_IN_MINUTES = 10  # Time step duration [min]
# Number of operation time steps [/]
N_PERIODS_PER_DAY = 24 * 60 / RESOLUTION_IN_MINUTES 
INVESTMENT_HORIZON = 20  # [Years] Investment horizon
DISCOUNT_RATE = 0.  # Discount rate [/] for computation of NPV

# Storage capacity
STORAGE_UNIT_CAPACITY = 90  # [Ah]
STORAGE_UNIT_VOLTAGE = 12  # [V]
STORAGE_UNIT_PRICE = 400  # [EUR]
# [/], means max current is 2 * STORAGE_UNIT_CAPACITY [A]
STORAGE_MAX_C_RATE = 2
INITIAL_SOC = 0  # Currently cot used [Wh]
CHARGE_EFFICIENCY = 0.95  # [/]
DISCHARGE_EFFICIENCY = 0.95  # [/]
BATERRY_USAGE_FEE = 0.01  # [EUR/kWh]

# Inverter capacity
INVERTER_UNIT_CAPACITY = 1000  # [VA]
INVERTER_UNIT_PRICE = 250  # [EUR]

# PV
PV_CAPACITY_PRICE = 0.4  # [EUR/Wp]
MAX_PV_CAPACITY = 10000  # [Wp]

# Grid connection cost
# Key: [A], value: [EUR]
GRID_CAPACITY_PRICE = {16: 1000, 32: 2500, 64: 6000}
GRID_VOLTAGE = 230  # [V]
GRID_IMPORT_PRICE = 0.28  # [EUR/kWh]
GRID_EXPORT_PRICE = 0.0  # [EUR/kWh]

# Genset
GENSET_CAPACITY_PRICE = {3100: 450, 5500: 750,
                         8000: 2880}  # Key: [VA], value: [EUR]
FUEL_PRICE_COEFF = 0.19  # [EUR/kWh]