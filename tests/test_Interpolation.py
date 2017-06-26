# -*- coding: utf-8 -*-
"""
Created on Tue Mar 01 18:38:20 2016

@author: alr
"""
import unittest
import numpy as np
from pyAPP6Tools import Interpolation

    
class TestFiles(unittest.TestCase):
 
    def setUp(self):
        pass

    def test_linint(self):
        self.assertEqual(Interpolation.linint(0.5,0.0,1.0,0.0,1.0),0.5)

    def test_linint_error(self):
        with self.assertRaises(ValueError):
            Interpolation.linint(0.5,0.0,0.0,0.0,1.0)

    def test_linint_error_nonstrict(self):
        self.assertEqual(Interpolation.linint(0.5,0.0,0.0,0.0,1.0,strict=False),0.0)

    def test_interp1dEx_linear(self):
        numpyTable=np.array([[0.0,0.0],[1.0,0.0]])
        x=0.5
        yi=Interpolation.interp1dEx(x, numpyTable, kind='linear')
        self.assertEqual(yi,0.0)
        
    def test_interp1dEx_linearEx(self):
        numpyTable=np.array([[0.0,0.0],[1.0,1.0]]) #[x,y] , [x2,y2]
        x=-1.0
        yi=Interpolation.interp1dEx(x, numpyTable, kind='linear')
        self.assertEqual(yi,-1.0)
        
    def test_interp1dEx_splineEx(self):
        numpyTable=np.array([[0.0,0.0],[1.0,1.0]]) #[x,y] , [x2,y2]
        x=-1.0
        yi=Interpolation.interp1dEx(x, numpyTable, kind='spline')
        self.assertEqual(yi,-1.0)