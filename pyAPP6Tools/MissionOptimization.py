# -*- coding: utf-8 -*-
"""
This module provides a function and classes for optimizing APP missions.

The optimizer depends on scipy and the mission computation on APP and
the pyAPP6 package

Copyright 2016, ALR
"""
#pylint: disable-msg=C0103

from __future__ import print_function
import copy, os
from scipy import optimize
import numpy as np
from pyAPP6 import Mission, Files

Nfeval = 0
state_list = []

def optimizeMission(misfile, segParList, misObjective, tol=1e-3, method='Nelder-Mead'):
    '''
    Function to optimize the parameter of a mission. The optimized mission will
    be saved with the filename "misfile" with a "_optTmp" suffix.

    Arguments
    ---------
    misfile : str
        path to the APP6 .mis file
    segParList : list[segmentParameter]
        list of segmentParameter class instances
    misObjective : missionObjective
        instance of a missionObjective class
    tol : float
        tolerance, see scipy.optimize.minimize
    method : str
        optimization method, see scipy.optimize.minimize

    Returns
    -------
    OptimizeResult
        The optimization result represented as a OptimizeResult object. See the
        documentation of scipy.optimize.minimize

    Examples
    --------
    This is a minimal Example on how to optimize two altitudes::

        misfile = r'myMission.mis'

        segParList = [segmentParameter(1, 8000.0, updateEndCondition),
                      segmentParameter(9, 11000.0, updateEndCondition)]

        objective = missionObjective('Distance', resFunctionMinimizeEndValue, mode='max')

        res = optimizeMission(misfile=misfile, segParList=segParList, misObjective=objective)
    '''
    global Nfeval, state_list

    misCmp0 = Mission.MissionComputation()
    misCmp0.run(misfile)
    misObjective.setNorm(misCmp0.result)

    #parameter
    Nfeval = 0
    state_list = []
    endValueList = len(segParList)*[1.0]

    res = optimize.minimize(_evaluateMis,
                            method=method,
                            x0=endValueList,
                            args=(misfile, segParList, misObjective), tol=tol, callback=_myCallback)
    if res['success']:
        _evaluateMis(res['x'], misfile, segParList, misObjective)
        suffix = '_optTmp'
        filepath, ext = os.path.splitext(misfile)
        modpath = filepath+suffix+ext
        print('Done. Output written to', modpath)
    return res

class segmentParameter(object):
    def __init__(self, idx, value, func):
        self.startValue = value
        self.segIdx = idx
        self.func = func
    def __call__(self, seg, x):
        return self.func(seg, x*self.startValue)

def updateEndCondition(seg, x):
    '''
    Input function "end condition 1"
    To be used as func input segmentParameter
    '''
    seg.endValue1.xx = x

def updateClimbAngle(seg, x):
    '''
    Input function "climb angle"
    To be used as func input segmentParameter
    '''
    seg.segFd.climb.xx = x

class missionObjective(object):
    def __init__(self, variable, func, mode='max'):
        self.value = None
        self.func = func
        self.variable = variable
        self.mode = mode
    def __call__(self, result):
        if self.mode == 'max':
            return self.value/self.func(result, self.variable)
        else:
            return self.func(result, self.variable)/self.value
    def setNorm(self, result):
        if self.value is None:
            self.value = self.func(result, self.variable)

def resFunctionMinimizeEndValue(misResult, variable):
    '''
    Objective function "mission end value"

    To be used as func in missionObjective
    '''
    try:
        idx_dst = misResult.getVariableIndex(variable)
        seg = misResult.getSegmentList()[-1]
        retVal = seg.getData()[-1, idx_dst]
    except:
        return np.nan
    return retVal
    
def _myCallback(xk):
    '''Helper function for optimizeMission. Don't call directely.
    '''
    global Nfeval
    global state_list
    state_list.append(copy.copy(xk))
    print('iteration', Nfeval, xk)
    Nfeval += 1

def _evaluateMis(x, mispath, segParList, misObjective):
    '''Helper function for optimizeMission.  Don't call directely.
    '''
    #read mission file
    suffix = '_optTmp'
    filepath, ext = os.path.splitext(mispath)
    modpath = filepath+suffix+ext
    misFile = Files.MissionComputationFile.fromFile(mispath)
    segList = misFile.getSegmentList()

    #loop through all segments and update parameter
    for p, xval in zip(segParList, x):
        seg = segList[p.segIdx]
        p(seg, xval) #updates segment

    #save modified mission file
    misFile.saveToFile(modpath, overwrite=True)

    #run modified mission file
    misCmp = Mission.MissionComputation()
    misCmp.run(modpath)

    #compute objective function and return result
    retVal = misObjective(misCmp.result)
    return retVal
