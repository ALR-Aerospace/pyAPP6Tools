# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 16:07:01 2016

@author: alr
"""
#pylint: disable-msg=C0103

import numpy as np
from pyAPP6.Files import X2Table

def addArraysToX3Table(a, b, c, d, x3table_output, clear_table=True):
    '''
    Reformats and adds the arrays a, b, c and d to a pyAPP X3Table
    
    This function is useful to convert CPACS or GasTurb propulsion output into
    the APP format.

    .. note::
        For propulsion data, (a,b,c,d) would correspond to (alt, Mach, thrust, fuelflow),
        and the x3table_output corresponds to an APP fuel flow table

    Arguments
    ---------
    a : ndarray
        numpy array of shape (N,2) (altitudes)
    b : ndarray
        numpy array of shape (N,2) (Mach numbers)
    c : ndarray
        numpy array of shape (N,2) (thrust values)
    d : ndarray
        numpy array of shape (N,2) (fuel flow values)
    x3table_output : pyAPP6.Files.X3Table
        X3Table to fill with a, b, c and d
    clear_table : bool
        if True, the x3table_output is cleared (default)

    '''
    if clear_table:
        x3table_output.clear()

    alist = restructureArrayData(a, b, c, d)

    for alt, a_table in alist:
        m_t_ff_table = X2Table(embedded=True)
        x3table_output.insertTable(alt, m_t_ff_table)
        for m, m_table in a_table:
            m_t_ff_table.insertTable(m, m_table)

def restructureArrayData(a, b, c, d):
    '''
    Helper function to convert data.

    Takes numpy arrays in the form (a,b,c,d) and reorders it into a
    nested list with (a,(b,(c,d))). The arrays a,b,c,d all have to be of shape (N,)

    .. note::
        For APP propulsion data, (a,b,c,d) would correspond to (alt, Mach, thrust, fuelflow),
        resulting in a nested list with shape (alt,(Mach,(thrust, fuelflow)))

    Arguments
    ---------
    a : ndarray
        numpy array of shape (N,2)
    b : ndarray
        numpy array of shape (N,2)
    c : ndarray
        numpy array of shape (N,2)
    d : ndarray
        numpy array of shape (N,2)

    Raises
    ------
    ValueError
        If the arrays are not of equal length

    Returns
    -------
    list
        nested list with shape [a, [b, [c, d]]]
    '''

    length = len(a)
    if any(len(lst) != length for lst in [b, c, d]):
        raise ValueError('input arrays must have same length')

    result = [] #resulting list with content (a,(b,(c,d)))

    unique_a = np.unique(a) #find all unique a values (e.g. altitudes)
    for element_a in unique_a:
        #extract all values at altitude *alt*
        b_tmp = b[a == element_a]
        c_tmp = c[a == element_a]
        d_tmp = d[a == element_a]

        #create and add sublist with content (m,(T,FF))
        m_list = []
        result.append([element_a, m_list])

        #loop through b (mach numbers) at values for a (altitude)
        for m in np.unique(b_tmp):
            #extract all values at altitude *alt* and mach number *m*
            ff_m = d_tmp[b_tmp == m]
            t_m = c_tmp[b_tmp == m]
            t_ff_array = np.vstack([t_m, ff_m]).T
            t_ff_array = t_ff_array[np.argsort(t_ff_array[:, 0])] #sorted numpy array with content (T,FF)
            m_list.append([m, t_ff_array])

    return result

def convertX3TableToArrays(x3table):
    '''
    Reformats a pyAPP X3Table into array form (a, b, c, d)
    
    This function is useful to convert APP data into CPACS format.
    
    .. note::
        For propulsion data, the x3table corresponds to an APP fuel flow table 
        and the output (a,b,c,d) would correspond to (alt, Mach, thrust, fuelflow).

    .. note::
        Loss of data can occur when converting from APP to CPACS, since the Max.
        Thrust Values tables of APP do not exist in CPACS. Make sure to append
        these values to the ouput array, or trim the output values accordingly.

    Arguments
    ---------
    x3table : pyAPP6.Files.X3Table
        X3Table instance with the data to convert

    Returns
    -------
    tuple
        a tuple (a,b,c,d) containing numpy arrays with equal length
    '''

    a_list = [] #Alt
    b_list = [] #Mach
    c_list = [] #Thrust
    d_list = [] #Fuel Flow

    for val_a, tab_x2 in zip(x3table.value, x3table.table):
        for val_b, tab_x1 in zip(tab_x2.value, tab_x2.table):
            thrust = tab_x1[:, 0]
            ff = tab_x1[:, 1]
            alt = [val_a] * len(thrust)
            Mach = [val_b] * len(thrust)
            a_list.extend(alt)
            b_list.extend(Mach)
            c_list.extend(thrust)
            d_list.extend(ff)

    #convert to numpy arrays (creates copy)
    a = np.array(a_list)
    b = np.array(b_list)
    c = np.array(c_list)
    d = np.array(d_list)

    return a, b, c, d
