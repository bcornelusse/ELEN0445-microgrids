# ELEN0445 Microgrids

This microgrids course is given at the Master's level at ULiège.
The goal of this course is to be applied and practical, with lab visits and sizing of installations.

Prerequisites: 
 - Notions of electrical circuits analysis (https://github.com/bcornelusse/livre_circuits_electriques_ELEC0053/)
 - Notions of optimization / mathematical programming
 - Notions of scientific computing (we will use Python)

Instructor: 
 - Bertrand Cornélusse

Teaching assistant:
 - Thomas Stegen
 - Clément Moureau

# Lectures of 2024-2025
|	 Date 	|	 Lecture 	|	 Topic 	|
|	 --- 	|	 --- 	|	 --- 	|
|	 	|	 	|	 **Microgrid architecture  and components module** 	|
|	 September 18 	|	1	|	 [Introduction lecture](https://bcornelusse.github.io/ELEN0445-microgrids/?p=introduction.md), [pdf](pdf/introduction.pdf) version, link to the [video](https://vimeo.com/458482575/aff88eb6bf) (2020) 	|
|	 September 25 	|	2	|	 [Lecture: Generation devices and power electronics interfaces](https://bcornelusse.github.io/ELEN0445-microgrids/?p=devices_and_interfaces.md), [pdf](pdf/devices_and_interfaces.pdf) version, link to the [video](https://vimeo.com/463509021/fd2d2a877e) (2020)	|
|		|		|	 [Lecture: Storage](https://bcornelusse.github.io/ELEN0445-microgrids/?p=storage.md) (prerecorded), [pdf](pdf/storage.pdf) version, link to the [video](https://vimeo.com/463823298/f6561ddd30) (2020) 	|
|		|		|	 Hands-on session: [Design a PV+storage installation with SMA sunny explorer tool](https://docs.google.com/document/d/11-PIfuOZclRARQJjPJf0fZI5lZdYmYdIg44CfuEL6Ss/edit?usp=sharing)	|
|	 October 2 	|	3	|	  [Lecture: Microgrid architectures - overview of controllers functions](https://bcornelusse.github.io/ELEN0445-microgrids/?p=architectures.md), [pdf](pdf/architectures.pdf) version	|
|	              	|	   	|	Assignment 1: lab microgrid visit and description (submit on ecampus, deadline: October 11.)	|
|		|		|	 **Control module**	|
|	 October 9    	|	4	|	  [Lecture: PV inverter control](pdf/20220927_PV_inverter_control.pdf) 	|
|	              	|	 	|	  [Lecture: Frequency and voltage control](https://bcornelusse.github.io/ELEC0447-analysis-power-systems/?p=lecture9_frequency_control_2023_bcr.md#1) ([pdf](https://bcornelusse.github.io/ELEC0447-analysis-power-systems/pdf/lecture9_frequency_control_2023_bcr.pdf)) |
|	              	|	   	|	 Assignment 2 (**TO BE UPDATED**): implement a solar MPTT algorithm ([description](pdf/HW2/MG_HW2_2023.pdf) and [files](pdf/HW2/MG_HW2_2023.zip)), submission on ecampus deadline: October 13	|
|	 October 16   	|	5	|	 Q&A on assignment 2	|
|	 October 23  	|	6	|	 Assignment 3 (**TO BE UPDATED**): controller of an islanded microgrid ([files](pdf/HW3/MG_HW3_v2.zip)), submission on ecampus deadline: November 27	|
|	 November 6  	|	7	|	Presentation of assignment 2 by students  	|
|		             |		 | Q&A assignment 3)		|
|	 	|	 	|	**Microgrid Optimization module**	|
|	 November 13  	|	8	|	 [Introduction to the optimization module](pdf/20211116_microgrids_optimization.pdf) 	|
|	              	|	   	|	 [Introduction to mathematical programming](pdf/intro_math_programming_v2.pdf) 	|
|	              	|	   	|	 [LP example 1 notebook](https://colab.research.google.com/drive/1xgO3EhGoG6P5E9BVV7QyPgLJM5HdNDrY?usp=sharing), [LP example 2 notebook](https://colab.research.google.com/drive/1ujoTNfu2_sCoVK7ksqbXgusmAAizvIip?usp=sharing) 	|
|	              	|	   	|	 MIP modeling exercises: [exercises pdf](pdf/MIP_exercises.pdf), [exercise 1 notebook](https://colab.research.google.com/drive/1dVQyXylIrwJvaD23hY2p1_xkplJfROqm?usp=sharing), [exercise 2 notebook](https://colab.research.google.com/drive/1UoUrG6N2I5RxA5g0IpXCH09gnsGybezG?usp=sharing) 	|
|	              	|	   	|	  2020 recordings: [linear programming](https://vimeo.com/470341870/615ef20e80), [MILP](https://vimeo.com/470525624/7fdaadad42) <br> [Python notebooks](notebooks/) 	|
|	              	|	   	|	  Presentation of Assignment 3 by students. 	|
|	 November 20   	|	9	|	 [From real-time control to microgrid sizing ](https://github.com/bcornelusse/ELEN0445-microgrids/blob/master/pdf/20211124_microgrids_optimization.pdf) 	|
|	              	|	    	|	 Assignment 4 statement ([description](pdf/HW4/MG_HW4_2023.pdf) and [files](pdf/HW4/HW4_2023.zip)) 	|
|	 November 27 	|	10	|	 End of microgrid optimization module. 	|
|	              	|	    	|	 Q&A assignment 4. 	|
|	              	|	    	|		|
|	 	|	 	|	**Forecasting module**	|
|	 December 4 	|	11	|	 [A quick introduction to machine learning](pdf/IntroductiontoMachineLearningDENSYS2021.pptx)	|
|	               	|	    	|	 Exercise: [room occupancy prediction](https://colab.research.google.com/drive/1qhVUg9_W-4U3AcQXyP9ZW7TfmbUX91Mz?usp=sharing) and [data](notebooks/data.zip)	|
|	 December 11 	|	12	|	 Introduction to forecasting, lecture-1 available (pdf and video) on [https://github.com/jonathandumas/ELEN0445-1-microgrids-forecasting](https://github.com/jonathandumas/ELEN0445-1-microgrids-forecasting)	|
|	               	|	    	|	 [Google colab](https://colab.research.google.com/drive/1D8gmKo97XKhXqa4pfUJRfSF4Hpy--8B7?usp=sharing) and [data](notebooks/data.csv) 	|
|	              	|	    	|	 [Hands on session: Load point forecast](pdf/hw4.pdf). Data and code template available on ecampus.	|
|	 December 18  	|	13	|	 Presentation of assignment 4 by students. 	|
|	 January exam session  	|	  	|	If needed.	|




# talk-template

This a fork of the talk template https://github.com/glouppe/talk-template from Gilles Louppe, that uses [remark](https://github.com/gnab/remark) for rendering slides from markdown, [KaTeX](https://github.com/Khan/KaTeX) for typesetting TeX equations, and some customised CSS.

## Instructions for editing

- Clone this repository and move in this repository
- Start an HTTP server to serve the slides:
```
python -m http.server 8001
```
- Edit `lectureX.md` for making your slides.
- Use [decktape](https://github.com/astefanutti/decktape) for exporting slides to PDF.

## Markup language

Slides are written in Markdown. See the remark [documentation](https://github.com/gnab/remark/wiki/Markdown) for further details regarding the supported features.

This template also comes with grid-like positioning CSS classes (see `assets/grid.css`) and other custom CSS classes (see `assets/style.css`)

## Integration with GitHub pages

Slides can be readily integrated with [GitHub pages](https://pages.github.com/) by hosting the files in a GitHub repositery and enabling Pages in the Settings tab.

See e.g. [https://glouppe.github.io/talk-template](https://glouppe.github.io/talk-template). 
