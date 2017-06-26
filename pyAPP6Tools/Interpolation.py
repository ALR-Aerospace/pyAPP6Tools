# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 09:36:38 2016

@author: alr
"""
#pylint: disable-msg=C0103

import numpy as np
from scipy.interpolate import interp1d

def linint(x, x0, x1, y0, y1, strict=True):
    '''
    linear interpolation or extrapolation for x, given the points (x0, y0), (x1, y1)

    Parameters
    ----------
    x : float
        the x-coordinate of the interpolated value
    x0 : float
        first x value of line
    x1 : float
        second x value of line
    y0 : float
        first y value of line
    y1 : float
        second y value of line
    strict : bool
        Defines if an exception should be raised if x0 == x1.
        If strict == False, y0 is returned

    Returns
    -------
    float
        interpolated y value at point x

    Raises
    ------
    ValueError
        If x0 == x2 and strict == True
    '''
    dx = float(x0)-float(x1)

    if dx == 0.0:
        if strict:
            raise ValueError('interpolation not possible: x0 == x1')
        else:
            return y0

    m = (float(y0)-float(y1))/dx
    y = m*(x-x0)+y0
    return y

def interp1dEx(x, numpyTable, kind='linear'):
    '''
    This function interpolates in a 2D numpy Table.
    x is the value to be interpolated.

    The interpolation type is defined by the string kind, use 'linear' or
    'spline' to reproduce the interpolation as in APP.

    For orther interpolation types, see the documentation of
    scipy.interpolate.interp1d

    .. note::
        extrapolation is always performed linearly

    Parameters
    ----------
    x : float
        x value to interpolate
    numpyTable : ndarray
        numpy array with shape (N,2)
    kind : str
        interpolation type, 'linear' or 'spline' for APP interpolation

    Returns
    -------
    float
        interpolated value
    '''
    #Check if table has more than one element:
    #otherwise interp1d would raise an error
    if len(numpyTable) <= 1:
        #Do linear extrapolation on this only value
        return numpyTable[0, 1]
    else:
        #Do linear Interpolation
        if np.min(numpyTable[:, 0]) <= x <= np.max(numpyTable[:, 0]):
            if kind == 'spline':
                return intrpltSpline(numpyTable[:, 0], numpyTable[:, 1], x)
            else:
                f = interp1d(numpyTable[:, 0], numpyTable[:, 1], kind=kind)
            return float(f(x))
        else:
            return _extrap1d(x, numpyTable)

def _extrap1d(x, numpyTable):
    '''Helper function for linear extrapolation

    This function extrapolates linear a value x upwards or downwards in a numpy Table
    '''
    #Find out if it is extrapolation up or down
    if x < numpyTable[0, 0]:
        return linint(x, numpyTable[1, 0], numpyTable[0, 0], numpyTable[1, 1], numpyTable[0, 1])
    elif x > numpyTable[-1, 0]:
        return linint(x, numpyTable[-1, 0], numpyTable[-2, 0],
                      numpyTable[-1, 1], numpyTable[-2, 1])

def interp2dEx(x, y, xList, npTable2d, kind_x='linear', kind_y='linear'):
    '''
    Interpolates and extrapolates in a 2d Table: z = f(x, y)
    x and y are the desired values. xList is the List of x values and
    npTable2d is a list of numpy-1d-arrays (y, z), each array corresponding to the x value.

    Parameters
    ----------
    x:
        Desired x value
    y:
        Desired y value
    xList:
        List of all x values
    npTable2d:
        List of numpy-1d-arrays (y, z), each array corresponding to the x value in xList.
    kind_x:
        kind of interpolation for variable x. (see documentation of scipy.interpolate.interp1d)
    kind_y:
        kind of interpolation for variable y. (see documentation of scipy.interpolate.interp1d)

    Returns
    -------
        the interpolated/extrapolated z value.
    '''
    xzTableTemp = []
    for xtemp, Table in zip(xList, npTable2d):
        ztemp = interp1dEx(y, Table, kind=kind_y)
        xzTableTemp.append([xtemp, ztemp])
    xzTable = np.array(xzTableTemp)
    return interp1dEx(x, xzTable, kind=kind_x)


def interp3dEx(x, y, z, xList, yztDataList, kind_x='linear', kind_y='linear', kind_z='linear'):
    '''
    Interpolates and extrapolates in a 3d Table: t = f(x, y, z)
    x, y and z are the desired values. xList is the List of x values and
    yzDataList is a list of [yList, list of numpy-1d-arrays (z, t)] elements

    Parameters
    ----------
    x:
        Desired x value
    y:
        Desired y value
    z:
        Desired z value
    xList:
        List of all x values
    yztDataList:
        List of [yList, list of numpy-1d-arrays (z, t)] elements,
        each element corresponding to the x value in xList.
        yList is a List of y values where each of the values is corresponding
        to its numpy-1d-array (z, t).
    kind_x:
        kind of interpolation for variable x. (see documentation of scipy.interpolate.interp1d)
    kind_y:
        kind of interpolation for variable y. (see documentation of scipy.interpolate.interp1d)
    kind_z:
        kind of interpolation for variable y. (see documentation of scipy.interpolate.interp1d)

    Returns
    -------
        the interpolated/extrapolated t value.
    '''
    xtTableTemp = []
    for xtemp, yzData in zip(xList, yztDataList):
        ttemp = interp2dEx(y, z, yzData[0], yzData[1], kind_x=kind_y, kind_y=kind_z)
        xtTableTemp.append([xtemp, ttemp])
    xtTable = np.array(xtTableTemp)

    return interp1dEx(x, xtTable, kind=kind_x)#, xtTable

def naturalSpline(vecX, vecY):
    '''
    calculates the spline coefficients for a natural spline interpolation, as
    implemented in the function intrpltSpline.
    Ported from APP 6.0 C++ code. Do not change.
    '''
    rows = len(vecX)

    vecU = np.zeros_like(vecX)
    vecS = np.zeros_like(vecX)

    vecU[0] = 0.0
    vecS[0] = 0.0

    #checkOrderedVector(vecX)

    for i in range(1, rows-1):
        sig = (vecX[i] - vecX[i-1]) / (vecX[i+1] - vecX[i-1])
        p = sig * vecS[i-1] + 2.0

        vecS[i] = (sig - 1.0) / p
        vecU[i] = (vecY[i+1] - vecY[i]) / (vecX[i+1] - vecX[i]) - (vecY[i] - vecY[i-1]) / (vecX[i] - vecX[i-1])
        vecU[i] = (6.0 * vecU[i] / (vecX[i+1] - vecX[i-1]) - sig * vecU[i-1]) / p

    vecS[rows-1] = 0.0

    for k in range(0, rows-1)[::-1]:
        vecS[k] = vecS[k] * vecS[k+1] + vecU[k]

    return vecS

def checkOrderedVector(vecX):
    for i in range(len(vecX)-1):
        if vecX[i] >= vecX[i+1]:
            return False
        return True

def intrpltSpline(vecX, vecY, x, vecS=None):
    '''
    Natural spline interpolation.
    Provide vecS computed by naturalSpline for faster interpolation.
    Ported from APP 6.0 C++ code. Do not change.
    '''
    EPSILON = 1e-4

    if vecS is None:
        vecS = naturalSpline(vecX, vecY)

    j = _locateIndex(vecX, x)
    h = vecX[j+1] - vecX[j]
    if h == 0.0:
        h = EPSILON
    a = (vecX[j+1] - x) / h
    b = (x - vecX[j]) / h

    if (a > 0.0) and (b > 0.0):
        return a*vecY[j] + b*vecY[j+1] + ((a**3.0-a)*vecS[j] + (b**3.0-b)*vecS[j+1]) * (h**2.0)/6.0
    else:
        return a*vecY[j] + b*vecY[j+1]

def _locateIndex(vecX, x):
    '''
    locate array index
    Used in intrpltSpline
    Ported from APP 6.0 C++ code. Do not change.
    '''
    rows = len(vecX)
    if x >= vecX[-1]:
        return rows-2
    if x <= vecX[0]:
        return 0
    j = np.where(vecX < x)[0][-1]
    return j