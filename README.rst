===============================
pyAPP6Tools
===============================

Community extensions to the ALR pyAPP6 Python module. Infomation on APP and pyAPP6 can be found here: http://aircraftperformance.software/pyapp/

.. image:: https://travis-ci.org/ALR-Aerospace/pyAPP6Tools.svg?branch=master
    :target: https://travis-ci.org/ALR-Aerospace/pyAPP6Tools

.. image:: https://coveralls.io/repos/github/ALR-Aerospace/pyAPP6Tools/badge.svg?branch=master
    :target: https://coveralls.io/github/ALR-Aerospace/pyAPP6Tools?branch=master


Installation
============

The pyAPP6Tools are installed the same way as pyAPP6. Please follow the directions given here: http://aircraftperformance.software/pyapp6/introduction.html#installation

Package Structure
===================

The pyAPP6Tools package comprises the following modules:

Atmosphere
    Functions to get data from the International Standard Atmosphere (ISA)

CPACS
    Functions to convert between CPACS and APP

Interpolation
    Functions to interpolate and extrapolate in 2D and 3D tables,
    using the APP6 interpoation functions.

MissionOptimization
    Functions to optimize APP6 mission parameter using scipy optimiztaion
    
Examples
===================

In the folder *Examples*, python scripts are given to demonstrate features of the modules