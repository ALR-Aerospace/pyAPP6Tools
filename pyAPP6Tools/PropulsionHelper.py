# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 09:22:02 2014

@author: ALR
"""
#pylint: disable-msg=C0103

import numpy as np
from pyAPP6.Files import X2Table, X3Table

def getMaxThrustFromFuelData(fuelTable, maxThrustTable):
    '''
    This function creates data for the maximum thrust as a function of altitude
    and Mach number from an APP fuel flow dataset. The resulting table is written
    into the maxThrustTable parameter.
    
    Parameters
    ----------
    fuelTable : pyAPP6.Files.X3Table
        instance of a fuel flow table, e.g. the fuelTable variable of a
        pyAPP6.Files.JetFuel instance
    maxThrustTable : pyAPP6.Files.X2Table
        instance of a max. thrust table, e.g. the maxThrustTable variable of
        a pyAPP6.Files.JetThrust instance
    '''
    maxThrustTable.clear()
    count1 = 0
    for h in fuelTable.value:
        table = []
        count2 = 0
        for j in fuelTable.table[count1].value:
            MaxThrust = fuelTable.table[count1].table[count2][0, 0]
            for k in fuelTable.table[count1].table[count2][:, 0]:
                if k > MaxThrust:
                    MaxThrust = k
            table.append([j, MaxThrust])
            count2 += 1
        numpytable = np.array(table)
        maxThrustTable.insertTable(h, numpytable)
        count1 += 1

