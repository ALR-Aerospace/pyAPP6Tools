# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 18:40:30 2017

@author: alr
"""
#pylint: disable-msg=C0103
import unittest
import mock


import numpy as np
import test_pyAPP6Files


class TestTableHelper(unittest.TestCase):

    def setUp(self):
        pass

    def test_restructureArrayData_nonEqualArrays_shouldRaiseException(self):
        with mock.patch.dict('sys.modules', **{'pyAPP6' : test_pyAPP6Files,
                                'pyAPP6.Files' : test_pyAPP6Files}):
            from pyAPP6Tools import TableHelper
            
            a = np.array([0.0, 0.0, 0.0])
            b = np.array([0.0, 0.0, 0.0])
            c = np.array([0.0, 0.0, 0.0])
            d = np.array([0.0, 0.0])
            with self.assertRaises(ValueError):
                TableHelper.restructureArrayData(a, b, c, d)

    def test_restructureArrayData_Length(self):
        with mock.patch.dict('sys.modules', **{'pyAPP6' : test_pyAPP6Files,
                                'pyAPP6.Files' : test_pyAPP6Files}):
            from pyAPP6Tools import TableHelper
            
            a = np.array([0.0, 0.0, 0.0])
            b = np.array([0.0, 0.0, 0.0])
            c = np.array([1.0, 2.0, 3.0])
            d = np.array([0.5, 0.7, 0.9])
            res = TableHelper.restructureArrayData(a, b, c, d)
            self.assertEqual(len(res), 1)
