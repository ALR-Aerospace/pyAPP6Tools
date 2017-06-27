# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 10:36:27 2016

@author: alr
"""
#pylint: disable-msg=C0103

import numpy as np
from . import TableHelper, PropulsionHelper


def getVector(tixi, path):
    '''
    Helper function to convert a tixi XML vector into a numpy array
    '''
    n = tixi.getVectorSize(path)
    return np.array(tixi.getFloatVector(path, n))

def getAttributeNames(tixi, path):
    '''
    Helper function to convert a tixi XML attributes into a python list
    '''
    nAtt = tixi.getNumberOfAttributes(path)
    return [tixi.getAttributeName(path, k+1) for k in range(nAtt)]

def getXPathChildString(elementName, index):
    '''
    Helper function for XPath formatting.
    
    Note: In XPath, index start with 1

    Returns
    -------
    str
        XPath element name for child with index "index"
    '''
    if index == 0:
        raise ValueError("Index is 0. XPath uses 1-based indexing.")
    return '{0}[{1:d}]'.format(elementName, index)
