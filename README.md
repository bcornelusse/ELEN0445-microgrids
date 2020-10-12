# ELEN0445 Microgrids

This is a course on microgrids and local energy communities given at Master's level at ULiège.
This course is still **UNDER CONSTRUCTION** because the master in electrical engineering, focus on electric power and energy systems, has been reorganized. The goal of this course is to be applied and practical, with lab visits and a few manipulations, sizing of installations, etc.

Prerequisites: 
 - Notions of electrical circuits analysis (https://github.com/bcornelusse/livre_circuits_electriques_ELEC0053/)
 - Notions of optimization / mathematical programming
 - Notions of scientific computing (we will use Python)

Instructor: 
 - Bertrand Cornélusse

Teaching assistants:
 - Selmane Dakir
 - Jonathan Dumas

We will interact through eCampus (videos, notifications, homeworks, questions, etc.). 

# Lectures 

| Date | Topic |
| --- | --- |
| September 16 | Lecture 1: [Introduction](https://bcornelusse.github.io/ELEN0445-microgrids/?p=introduction.md), [pdf](pdf/introduction.pdf) version, link to the [video](https://vimeo.com/458482575/aff88eb6bf) |
| September 23 | Lecture 2: [Microgrid architectures - offgrid microgrid](https://bcornelusse.github.io/ELEN0445-microgrids/?p=architectures.md), [pdf](pdf/architectures.pdf) version, link to the [video](https://vimeo.com/461332158/b11a5a74c7) <br> Assignment: draw a schematic of the example board (see lecture slides, submit on ecampus)|
| September 30 | Lecture 3: [Generation devices and power electronics interfaces](https://bcornelusse.github.io/ELEN0445-microgrids/?p=devices_and_interfaces.md), [pdf](pdf/devices_and_interfaces.pdf) version, link to the [video](https://vimeo.com/463509021/fd2d2a877e)<br> Assignment 2: implement a solar MPTT algorithm  (submit on ecampus)|
| October 7 | Q&A session for assignment 2 <br> Lecture 4: [Storage](https://bcornelusse.github.io/ELEN0445-microgrids/?p=storage.md) (prerecorded), [pdf](pdf/storage.pdf) version, link to the [video](https://vimeo.com/463823298/f6561ddd30) |
| October 14 | Assignment 3 and Q&A session: design a PV+storage installation with SMA sunny explorer tool |
| October 21 | Lecture 5: [Introduction to mathematical programming](https://bcornelusse.github.io/ELEN0445-microgrids/pdf/intro_math_programming-v1.pdf) |
| October 28 | Lecture 6: [Demand side management](https://bcornelusse.github.io/ELEN0445-microgrids/pdf/ELEN0445-1-microgrids-4-operating_a_microgrid.pdf) (to be modified this year) <br> Assignment: home energy management| 
| November 18 | Lecture 7: [Microgrid sizing ](https://bcornelusse.github.io/ELEN0445-microgrids/pdf/ELEN0445-1-microgrids-5-sizing_a_microgrid-v3.pdf) (to be modified this year) <br> Assignment: home energy planning |
| November 25 | Lecture 8: [Forecasting](https://bcornelusse.github.io/ELEN0445-microgrids/pdf/20191002-ELEN0445-1-microgrids-forecasting-lesson.pdf) 
| December 2 | Lecture 9: Probabilistic forecasting (new this year) <br> Assignment: forecast PV generation |
| December 9 | Lecture 10: [Local energy communities](https://bcornelusse.github.io/ELEN0445-microgrids/pdf/ELEN0445-1-microgrids-6-community_microgrids-v4.pdf) (to be modified this year) |
| December 16 | If needed |


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
