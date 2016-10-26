# -*- coding: utf-8 -*-
"""
This module provides data for the international standard atmosphere (ISA) as
implemented in APP, through the two functions getAirState and getPressureAlt

Copyright 2016, ALR
"""

#pylint: disable-msg=C0103

import sys
import numpy as np

#define fixed parameters

i_max = 8

minH = -1000.0
maxH = +80.0e3
min_dT = -50.0
max_dT = +50.0

G = 9.80665
R = (8.31432e3 / 28.96442)
GAMMA = 1.4

Hi = [0.0, 11e3, 20e3, 32e3, 47e3, 51e3, 71e3, 80e3]
Li = [-6.5e-3, 0.0, 1.0e-3, 2.8e-3, 0.0, -2.8e-3, -2.0e-3, 0.0]
Ti = [288.15, 216.65, 216.65, 228.65, 270.65, 270.65, 214.65, 196.65]
pi = [1.013250e5, 2.263204e4, 5.474879e3, 8.680160e2, 1.109058e2, 6.693853e1,
      3.956392, 8.862722e-1]

def getAirState(alt, dT):
    '''
    Get the atmospheric properties of the international standard
    atmosphere (ISA) at a specified altitude.

    Arguments
    ---------
    alt : float
        Geometric altitude [m]
    dT : float
        Temperature offset from standard temperature [K]

    Returns
    -------
    tuple
        Tuple containing temperature [K], pressure [Pa], density [Kg/m^3],
        viscosity [Ns/(m^2)] and speed of sound [m/s]
    '''
    Hp = getPressureAlt(alt, dT)

    index = _getIndex(Hp)

    temp = _temperature(Hp, dT, index)
    Tisa = _temperature(Hp, 0.0, index)
    p = _pressure(Hp, Tisa, index)
    dens = _density(temp, p)
    mu = _dynamicViscosity(temp)
    a = _speedOfSound(temp)

    return temp, p, dens, mu, a

def getPressureAlt(alt, dT):
    '''
    Function to calculate the pressure altitude for a given temperature
    offset dT from the standard atmosphere.

    Arguments
    ---------
    alt : float
        Geometric altitude [m]
    dT : float
        Temperature offset from standard temperature [K]

    Returns
    -------
    float
        Pressure altitude [m]
    '''
    if alt > maxH or alt < minH:
        raise ValueError('Altitude Values out of Bounds')
    if dT > max_dT or dT < min_dT:
        raise ValueError('Temperature Values out of Bounds')
    if dT == 0.0:
        return alt
    else:
        po = pi[0]
        Hp = alt
        Hpold = sys.float_info.max

        counter = 0
        while (abs(Hp-Hpold) > 1) and (counter < 100):
            i = _getIndex(Hp)
            T = _temperature(Hp, 0.0, i)
            p = _pressure(Hp, T, i)

            Hpold = Hp
            Hp = alt + (R/G * dT * np.log(p/po))

            counter += 1
        return Hp

def _getIndex(Hp):
    '''
    Internal helper function to get current layer index

    Arguments
    ---------
    Hp : float
        pressure altitude [m]

    Returns
    -------
    int
        layer index
    '''
    if Hp < Hi[0]:
        return 0
    else:
        return np.where(np.array(Hi) <= Hp)[0][-1]

def _dynamicViscosity(temp):
    ''' Dynamic Viscosity according to Sutherland's empicial coefficients. See ESDU 77022.

    Arguments
    ---------
    temp : float
        Temperature [K]

    Returns
    -------
    float
        Dynamic Viscosity [Ns/m^2]
    '''
    return 0.1458*10.0**(-5.0)*temp**0.5/(1.0+110.4/temp)

def _density(temp, pressure):
    '''
    Internal function to calculate air density

    Arguments
    ---------
    temp : float
        Temperature [K]
    pressure : float
        Pressure [Pa]
    Returns
    -------
    float
        Density [kg/m^3]
    '''
    return pressure / R / temp

def _speedOfSound(temp):
    '''
    Internal function to calculate the speed of sound.

    Arguments
    ---------
    temp : float
        Temperature [K]

    Returns
    -------
    float
        Speed of sound [m/s]
    '''
    return (GAMMA * R * temp)**0.5

def _temperature(alt, dT, idx):
    '''
    Internal function to calculate air temperature for a given atmosphere layer.

    Arguments
    ---------
    alt : float
        pressure altitude [m]
    dT : float
        Temperature offset from standard temperature [K]
    idx : int
        index of atmosphere layer

    Returns
    -------
    float
        Temperature [K]
    '''
    T = Ti[idx] + dT + (Li[idx] * (alt - Hi[idx]))
    return T

def _pressure(alt, T_ISA, idx):
    '''
    Internal function to calculate the pressure at a given Layer

    Arguments
    ---------
    alt : float
        pressure altitude [m]
    T_ISA : float
        ISA Temperature [K]
    idx : int
        index of atmosphere layer

    Returns
    -------
    float
        pressure [Pa]
    '''
    if Li[idx] != 0:
        p = (Ti[idx] / T_ISA)**(G / R / Li[idx]) * pi[idx]
    else:
        p = np.exp(-(G/R * (alt - Hi[idx]) / Ti[idx])) * pi[idx]
    return p
