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
- we will dive in the details of the PV system installation

Side goals:
- evaluate the potential of the ULiège buildings
- compare to their consumption
- evauate the benefit of storage 

---

# Sizing to feed electricity to the grid

All the energy generated is fed to the grid at a given fee of 130 EUR / MWh.

Use an all-in cost of the PV installation of 800 EUR/kWp (relatively large installation).

No storage is needed.


---

## Choose a building

- **TODO** List of buildings 
- B28

---

## Design the installation using the 3D modeling tool

 - Delimit the surfaces
 - Place a maximum of PV panels

---

## Choose the inverters

 - Organize the PV strings to meet a trade-off between cost and energy-yield (for the amount of PV panels defined previously)
 - What are the constraints to connect the strings
 - What is a polystring configuration?
 - What is the minimal power rating of the inverter you can use for the given amount of PV panels ? What's his energy yield?

---

#  Sizing with self-consumtpion

 - **TODO** Obtain consumption data from ULiège’s buildings
 - Insert them in SMA sunny design web in a self-consumption design
 - Analyze the difference with the "feed to grid case"

---

# Sizing with storage and self-consumtpion

 - Redo the analysis and determine how much storage power / energy you would need as a function of the costs
 - use costs of 300 EUR/kWh andd 100 EUR/kW for the batteries

---

# Report

- Write a little report with your observations
- Include SMA sizing reports in a zip (with meaningful names for the different analyses).
