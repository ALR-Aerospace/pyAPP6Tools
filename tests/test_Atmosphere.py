# -*- coding: utf-8 -*-
"""
Created on Tue Mar 01 18:38:20 2016

@author: alr
"""
import unittest

from pyAPP6Tools import Atmosphere

class TestAtmosphere(unittest.TestCase):

    def setUp(self):
        pass

    def test_PressureAltitude_SLS(self):
        self.assertEqual(Atmosphere.getPressureAlt(0.0, 0.0), 0.0)
        
    def test_PressureAltitude(self):
        self.assertEqual(round(Atmosphere.getPressureAlt(20000.0, 10.0),5), 19183.50823) #copied from result
    
    def test_pressure_SLS(self):
        self.assertEqual(Atmosphere._pressure(0.0, 288.15, 0), 1.013250e5)

    def test_temperature_SLS(self):
        self.assertEqual(Atmosphere._temperature(0.0, 0.0, 0), 288.15)
        
    def test_speedOfSound_SLS(self):
        self.assertEqual(round(Atmosphere._speedOfSound(288.15),4), 340.294) #according to ESDU77022 
        
    def test_density_SLS(self):
        self.assertEqual(round(Atmosphere._density(288.15, 1.013250e5),4), 1.225) #according to ESDU77022
    
    def test_getAirstateAltBoundary(self):
        with self.assertRaises(ValueError):
            ret = Atmosphere.getAirState(90000,10.0)
    
    def test_getAirstateTempBoundary(self):
        with self.assertRaises(ValueError):
            ret = Atmosphere.getAirState(1999.0,60.0)

    def test_getAirstate(self):
        self.assertEqual(len(Atmosphere.getAirState(0.0,0.0)),5)
    