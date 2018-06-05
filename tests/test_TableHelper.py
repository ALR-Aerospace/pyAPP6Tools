# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 18:40:30 2017

@author: alr
"""
#pylint: disable-msg=C0103
import unittest
import sys
import mock

import numpy as np

#use mock to removed missing dependency from TableHelper
sys.modules['pyAPP6'] = mock.Mock()
sys.modules['pyAPP6.Files'] = mock.Mock()

from pyAPP6Tools import TableHelper

class TestTableHelper(unittest.TestCase):

    def setUp(self):
        pass

    def test_restructureArrayData_nonEqualArrays_shouldRaiseException(self):
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([0.0, 0.0, 0.0])
        c = np.array([0.0, 0.0, 0.0])
        d = np.array([0.0, 0.0])
        with self.assertRaises(ValueError):
            TableHelper.restructureArrayData(a, b, c, d)

    def test_restructureArrayData_Length(self):
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([0.0, 0.0, 0.0])
        c = np.array([1.0, 2.0, 3.0])
        d = np.array([0.5, 0.7, 0.9])
        res = TableHelper.restructureArrayData(a, b, c, d)
        self.assertEqual(len(res), 1)
