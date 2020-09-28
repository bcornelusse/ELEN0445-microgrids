class: middle, center, title-slide
count: false

# Microgrids

Microgrid power sources and power electronics interfaces

<br><br>

Bertrand Cornélusse<br>
[bertrand.cornelusse@uliege.be](mailto:bertrand.cornelusse@uliege.be)

---

## Content of this lecture

In this lecture we review 
- the main types of components that can be used as sources in microgrids
- their power electronics interfaces

---

class: middle, center
# Power electronics interfaces

---

## 3 main categories of power electronics devices

.grid[
.kol-1-2[
- Rectifiers: AC to DC, are typically used at the output of small wind turbines or micro-turbines<br><br><br><br>
- DC-DC converters e.g. to interface photovoltaic modules and achieve their maximum power operating point<br><br><br><br>
- Inverters: DC to AC e.g. to connect PV modules to the AC distribution grid
]
.kol-1-2[.width-80[![](figures/types_of_converters.png)]]
]

---

## The main components of power electronics devices

<br><br>

.center.width-80[**Controllable switches that can be actuated at a high frequency, without excessive losses, and with a large lifetime**]

<br><br>

.grid[
.kol-1-2[
Ideal switch model:
- no losses
- switches without delay
]
.kol-1-2[.width-100[![](figures/ideal_switch.png)]]
]

---

## Realistic switch model
<br><br><br>
.center.width-50[![](figures/ideal_switch.png)]

---

## Diode models: ideal diode

.center.width-80[![](figures/ideal_diode.png)]

- Current flows from anode to cathode when forward biased: $i>0 \Rightarrow v=0 $
- No current when reversed bias: $v<0 \Rightarrow i=0$

---

## Diode models: realistic diode in the forward bias region

.center.width-80[![](figures/piecewise_diode.png)]

Piecewise linear approximation of “true exponential model”.

---

## Thyristors

.center.width-20[![](figures/thyristor.png)]

Thyristors are “controllable diodes”, through a gate where a signal is applied

Different types:
- GTO (gate turn off) can be turned on and off, less than 1kHz switching frequency
- SCR (silicon-controlled rectifier): can be turned on, turns off when forward current goes through zero
- TRIAC (Triode alternating current): two SCR back to back with one gate (AC-AC conversion)

---

## Transistors

- Bipolar junction transistors (BJT)
 - Historically used as amplifiers in their active region of operation
 - Can also be used as a switch, in the saturation region
 - High power, but high losses
- Field effect transistors (MOSFET)
 - High speed and high efficiency at low voltage.
 - Isolated gate (field effect)
 - Commonly used for low voltage converters

---

## Insulated Gate Bipolar Transistor (IGBT)

- Most common device for high power DC-DC converters and inverters from medium to high voltages
- Combination of BJT and MOSFET
- Now replaces thyristors in most medium to high power applications

---

# Characterization of power electronics devices

*DC component*: 
- Integral of the output signal over a full AC input cycle.
- In case of a rectifier, this is the power that is really transmitted from source to load.

--

*Total Harmonic Distortion*:
THD = ratio of the total signal, including harmonics, to the desired frequency component:

$$THD = \sqrt{\frac{F^2\_{RMS}-F^2\_{RMS,1}}{F^2\_{RMS}}}$$

IEEE standard 519–1992, “Recommended Practices and Requirements for Harmonic Control in Electrical Power Systems”, states that the voltage THD is limited to 5% for general systems and is only up to 20% for dedicated systems

---

# Rectifiers
.center.width-30[![](figures/rectifiers.png)]

Rectifiers: large subclass of topologies for AC to DC conversion
- Single-phase or three phase voltage source to DC current load
- Power-electronic is “only” the front end:<br>
<br>
<br>
.center.width-100[![](figures/cascade.png)]

---

## Half bridge single phase topology

.center.width-90[![](figures/half_bridge_1P.png)]

DC component: $V\_{DC} = \frac{V_p}{2 \pi} \int_0^\pi \sin(t) dt = -\frac{V_p}{2 \pi} \cos(t)|\_0^\pi = \frac{V_p}{\pi}$

---

## Full-bridge single phase topology

.center.width-90[![](figures/full_bridge_1P.png)]

- DC component twice of the half bridge
- But Large harmonic current in the input AC current
- DC output not controllable

---

## Full-bridge single phase topology *with low pass filter*

.center.width-90[![](figures/full_bridge_1P_filter.png)]

- Improves output harmonics content
- Better if capacitor size increases
 - which in turn degrades harmonic content of input
- Bad power factor => LC topology
- Active power factor correction => DC-DC after the rectifier

---

## Recap with more realistic components

.center.width-100[![](figures/recap_rectifiers.png)]

---

# DC - DC converters

.center.width-30[![](figures/DCDC.png)]

- DC-DC converters are present in many devices,
 - from mW power level to MW level
- Made possible by MOSFET and IGBTs
- Can be unidirectional, from low voltage to high voltage or the inverse, or bidirectional
 - $v\_h > v\_l$, $i\_l>i\_h$

---

## Basic bloc: two switches

.center.width-100[![](figures/principle_DCDC.png)]


Only one switch ON at a time! 

---

## Pulse Width Modulation (PWM)

- Process that actuates the switches
- Duty cycle signal compared to a reference triangular waveform of a chosen frequency

.center.width-80[![](figures/pwm.png)]

---

## Converter types

.grid[
.kol-1-2[*BUCK*

q1 is a controllable switch and q2 is a diode
.center.width-80[![](figures/buck1.png)]
.center.width-80[![](figures/buck2.png)]]
.kol-1-2[*BOOST*

q2 is a controllable switch and q2 is a diode
.center.width-80[![](figures/boost1.png)]
.center.width-80[![](figures/boost2.png)]]
]

---

# Inverters

.center.width-30[![](figures/inverters.png)]

- Voltage source inverter: $v\_{AC} < v\_{DC}$
- Current source inverter: $v\_{AC} > v\_{DC}$
- Impedance source inverter : for a wide variation of $v\_{AC} \leq v\_{DC}$

.center.width-500[![](figures/principle_inverter.png)]

---


class: middle, center
# Power generation sources

---

class: middle, center
# Implementing a solar MPPT algorithm

---

## Assignment

By teams of 2, 

---

# References

- Kwasinski, Alexis, Wayne Weaver, and Robert S. Balog. Microgrids and other local area power and energy systems. Cambridge University Press, 2016.


---

class: end-slide, center
count: false

The end.
