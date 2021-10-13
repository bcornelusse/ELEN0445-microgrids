class: middle, center, title-slide
count: false

# Microgrids

PV system design using SMA sunny design web
<br><br>

Bertrand Cornélusse<br>
[bertrand.cornelusse@uliege.be](mailto:bertrand.cornelusse@uliege.be)

---

# Goals of this assignment

Learn how to size a PV system installation
- we will use a free tool from SMA: https://www.sunnydesignweb.com/
- we will dive into the details of the PV system installation

Side goals:
- evaluate the potential of the ULiège buildings
- compare to their consumption
- evaluate the benefit of storage

---

## 0. Choose a building

- B28
- B5a
- B7a
- B8
- B15
- B28
- B30
- B31
- B33
- B62

---

# 1. Sizing to feed electricity to the grid

All the energy generated is fed to the grid at a given fee of 130 EUR / MWh.

Use an all-in cost of the PV installation of 800 EUR/kWp (relatively large installation).

No storage is needed.

---

## Design the installation using the 3D modeling tool

 - Delimit the surfaces
 - Place a maximum of PV panels

---

## Choose the inverters

 - Organize the PV strings to meet a trade-off between cost and energy yield (for the amount of PV panels defined previously)
 - What are the constraints to connect the strings
 - What is a polystring configuration?
 - What is the minimal power rating of the inverter you can use for the given amount of PV panels? What is his energy yield?

---

#  2. Sizing with self-consumption

 - Get the consumption data from ULiège building assigned to you: https://dox.uliege.be/index.php/s/lKWKs02hQzuopm0
 - Insert them in SMA sunny design web in a self-consumption design
 - Analyze the difference with the "feed to grid case."
 - You buy electricity at 150 EUR/MWh
 - There is no net metering, it is a dual-flow meter

---

# 3. Sizing with storage and self-consumption

 - Redo the analysis and determine how much storage power/energy you would need as a function of the costs
 - use costs of 300 EUR/kWh and 100 EUR/kW for the batteries

---

# 4. Sizing with off-grid mode

 - Redo the analysis and determine how much storage power/energy and diesel generator you would need as a function of the costs
 - use costs of 300 EUR/kWh and 100 EUR/kW for the batteries

---

# Report

- Write a little presentation with your answers to the listed questions
- Include SMA sizing reports in a zip (with meaningful names for the different analyses).
