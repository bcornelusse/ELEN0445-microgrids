class: middle, center, title-slide
count: false

# Microgrids

Microgrid architectures

<br><br>

Bertrand Cornélusse<br>
[bertrand.cornelusse@uliege.be](mailto:bertrand.cornelusse@uliege.be)

---

# Content of this lecture

In this lecture we review microgrids architectures, that is which components form a microgrid and how to interconnect them.

In the next lectures we will focus on the components themselves, on features that are
important for operation, both from a technical point of view and from an economical point of view.


---

## AC grids

- Most microgrids are AC
- Most microgrids are three-phase!
 - Equipments in general require less components per unit of power transferred
 - Easy to generate a rotating field for motors
 - (Three-phase power transfer is a constant expression (if the phases are balanced))

---

## Power electronics

Power electronic circuits are interfaces
- between devices (DERs and loads) and the power distribution grid
- between the microgrid and the distribution grid (PCC)

Purpose: enable a controllable (bidirectional) flow between devices

---

## E.g. SMA three-phase inverter

TODO picture

Source: website of SMA

Requires a network signal


---

## E.g. Victron Multiplus - PCC & battery charger


Source: website of Victron


---

## E.g. Studer-innotec VarioString series

Source: website of Studer-innotec

---

## Automatic transfer switches
 

---

# DC microgrids

- The distribution system is DC
 - Requires DC to DC converters to adapt voltage to devices
 - DC to AC to power AC loads, or to inject in the public grid
 - AC to DC to convert AC generation to DC (e.g. from public grid to microgrid)
- DC microgrids are not widespread but gain some interest

---

## DC vs AC: pros

- DC systems enable a simpler integration of distributed energy resources (DERs*), since many of them are either DC by nature or require a DC interface anyway
- Parallel distributed architectures are simpler to realize in DC:
 - unnecessary frequency control and phase synchronization
- Frequency control is not necessary in DC systems
 - unwanted harmonic content may by easier to filter too


*DER: sources of electric power that are not directly connected to a bulk power transmission system. Distributed energy resources include both generators and energy storage technologies. (T.Ackermann, G.Andersson, and L.Söder, “Distributed Generation: A Definition,” Electric Power Systems Research, vol. 57, issue 3, April 2001, pp. 195–204.)

---

## DC vs AC: cons

- Autonomous distributed control harder in DC than in AC because no information carried through the signal (frequency, phase)
- There are stability issues due to DC-DC conversion stages
- It is more difficult to clear fault currents: the signal “does not go through zero”. Hence protections are more costly and harder to set up.

---

## Most common: radial architecture

- Subject to availability issues (one single path to a load)
- alternatives:
 - provide a redundant path to each load
 - provide spatially diverse paths
 - ring-type distribution
 - ladder type distribution

---

## Characterizing power distribution architectures based on how power conversion is performed

- Centralized: power conversion is performed at a single power electronic interface
- Distributed: power conversion functions are spread among converters
 - may lead to parallel or cascade structures

---

## Exemple 1 from Studer

TODO

---

## Exemple 2 from Studer

TODO

---

## Off grid case design

---

# Parts

- Solar charge controller (30 A)
- PV panel
- Battery
- Inverter (1500 W)

- Buses
- cables: 
 - inverter DC side: < 1m, 25 $mm^2$, up to 160 A (1920 VA)
 - solar charge controller, 1m, 6 $mm^2$, up to 40 A

- Fuses:



---

# References

- Kwasinski, Alexis, Wayne Weaver, and Robert S. Balog. Microgrids and other local area power and energy systems. Cambridge University Press, 2016.


---

class: end-slide, center
count: false

The end.
