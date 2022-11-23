# ELEN0445 Microgrids

This is a course on microgrids and local energy communities given at Master's level at ULiège.
The goal of this course is to be applied and practical, with lab visits and a few manipulations, sizing of installations, etc.

Prerequisites: 
 - Notions of electrical circuits analysis (https://github.com/bcornelusse/livre_circuits_electriques_ELEC0053/)
 - Notions of optimization / mathematical programming
 - Notions of scientific computing (we will use Python)

Instructor: 
 - Bertrand Cornélusse

Teaching assistant:
 - Thomas Stegen

We will interact through eCampus (videos, notifications, homeworks, questions, etc.). 


# Lectures of 2022-2023
| Date | Lecture | Topic |
| --- | --- | --- |
| | | **Microgrid architecture, components, and control** |
| September 14 | 1 | [Introduction lecture](https://bcornelusse.github.io/ELEN0445-microgrids/?p=introduction.md), [pdf](pdf/introduction.pdf) version, link to the [video](https://vimeo.com/458482575/aff88eb6bf) (2020) |
| September 21 | 2 |  [Lecture: Microgrid architectures - overview of controllers functions](https://bcornelusse.github.io/ELEN0445-microgrids/?p=architectures.md), [pdf](pdf/architectures.pdf) version|
|              |   |Assignment 1: lab microgrid visit and description (submit on ecampus, deadline: September 28.)|
| September 28 | 3 | [Lecture: Generation devices and power electronics interfaces](https://bcornelusse.github.io/ELEN0445-microgrids/?p=devices_and_interfaces.md), [pdf](pdf/devices_and_interfaces.pdf) version, link to the [video](https://vimeo.com/463509021/fd2d2a877e) (2020)|
|              |   |  [Lecture: PV inverter control](pdf/20220927_PV_inverter_control.pdf) |
|              |   | Assignment 2: implement a solar MPTT algorithm (description and submission on ecampus)|
| October 5    | 4 | Q&A on assignment 2 |
|              |   | [Lecture: Storage](https://bcornelusse.github.io/ELEN0445-microgrids/?p=storage.md) (prerecorded), [pdf](pdf/storage.pdf) version, link to the [video](https://vimeo.com/463823298/f6561ddd30) (2020) |
| October 12   | 5  | [Assignment 3: design a PV+storage installation with SMA sunny explorer tool ](https://docs.google.com/document/d/11-PIfuOZclRARQJjPJf0fZI5lZdYmYdIg44CfuEL6Ss/edit?usp=sharing) presentation and Q&A session|
||||
| | |**Forecasting module**|
| October 19   | 6  | [A quick introduction to machine learning](pdf/IntroductiontoMachineLearningDENSYS2021.pptx)|
|            |   | Exercise: [room occupancy prediction](https://colab.research.google.com/drive/1qhVUg9_W-4U3AcQXyP9ZW7TfmbUX91Mz?usp=sharing) and [data](notebooks/data.zip)|
| October 26  |  7  | Introduction to forecasting, lecture-1 available (pdf and video) on [https://github.com/jonathandumas/ELEN0445-1-microgrids-forecasting](https://github.com/jonathandumas/ELEN0445-1-microgrids-forecasting)|
|              |   | Presentation of assignment 2 by students. |
| November 9  | 8 | Introduction to probabilistic forecasting, lecture-2 available (pdf + video) on [https://github.com/jonathandumas/ELEN0445-1-microgrids-forecasting](https://github.com/jonathandumas/ELEN0445-1-microgrids-forecasting)  |
|              |    | [Assignment: Load point and probabilistic forecast](pdf/hw4.pdf). Data and code template available on ecampus.|
||||
| | |**Microgrid Optimization module**|
| November 16  | 9 | [Introduction to the optimization module](pdf/20211116_microgrids_optimization.pdf) |
|              |   | [Introduction to mathematical programming](pdf/intro_math_programming_v2.pdf) | 
|              |   | [LP example 1 notebook](https://colab.research.google.com/drive/1xgO3EhGoG6P5E9BVV7QyPgLJM5HdNDrY?usp=sharing), [LP example 2 notebook](https://colab.research.google.com/drive/1ujoTNfu2_sCoVK7ksqbXgusmAAizvIip?usp=sharing) | 
|              |   | MIP modeling exercises: [exercises pdf](pdf/MIP_exercises.pdf), [exercise 1 notebook](https://colab.research.google.com/drive/1dVQyXylIrwJvaD23hY2p1_xkplJfROqm?usp=sharing), [exercise 2 notebook](https://colab.research.google.com/drive/1UoUrG6N2I5RxA5g0IpXCH09gnsGybezG?usp=sharing) |
|              |   |  2020 recordings: [linear programming](https://vimeo.com/470341870/615ef20e80), [MILP](https://vimeo.com/470525624/7fdaadad42) <br> [Python notebooks](notebooks/) |
|              |   |  Presentation of Assignment 3 by students. |
| November 23  | 10 | [From real-time control to microgrid sizing ](https://github.com/bcornelusse/ELEN0445-microgrids/blob/master/pdf/20211124_microgrids_optimization.pdf) |
| November 30   | 11 | No lecture. Q&A session if needed. |
| December 7   | 12 | End of microgrid optimization module. |
|              |    | Assignment 5 statement (**TO BE UPDATED**) |
|              |    | Q&A assignment 4. |
| December 14   | 13 | Presentation of Assignment 4 by students. |
| January exam session  |  | Presentation of assignment 5 by students. |


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
