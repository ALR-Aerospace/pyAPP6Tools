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

def getAerodynamicDict(tixi, aeroPerformanceMapPath, RefArea):
    '''
    Gets aerodyanmic data from a cpacs file and prepares a dict ready for APP import.

    .. note::
        The transformation of forces from the cpacs system into the app system is only valid
        for the entries with beta=0.

    Parameters
    ----------
    tixi : tixiwrapper.Tixi
        instance of a Tixi object
    aeroPerformanceMapPath : str
        path to the xml node of the aeroPerformanceMap, usually this is
        '/cpacs/vehicles/aircraft/model/analyses/aeroPerformanceMap'
    RefArea : float
        aerodynamic reference area in m^2

    Returns
    -------
    dict
        containing the aerodynamic data in APP format
    '''
    sizes = tixi.getArrayDimensions(aeroPerformanceMapPath)
    aeroSize = tixi.getArrayDimensionSizes(aeroPerformanceMapPath, sizes)
    dimensionNames = tixi.getArrayDimensionNames(aeroPerformanceMapPath, sizes)

    aeroPerformanceMap = dict()
    for i, dimName in enumerate(dimensionNames):
        tixi.getArrayDimensionValues(aeroPerformanceMapPath, i, aeroSize[0][i])
        aeroPerformanceMap[dimName] = getVector(tixi, aeroPerformanceMapPath+'/'+dimName)

    #short variables
    Mach = aeroPerformanceMap['machNumber']
    Re = aeroPerformanceMap['reynoldsNumber']
    Beta = aeroPerformanceMap['angleOfYaw']
    Alpha = aeroPerformanceMap['angleOfAttack']

    aeroPerformanceMap['cfx'] = np.array(tixi.getArray(aeroPerformanceMapPath, 'cfx', aeroSize[1]))
    aeroPerformanceMap['cfy'] = np.array(tixi.getArray(aeroPerformanceMapPath, 'cfy', aeroSize[1]))
    aeroPerformanceMap['cfz'] = np.array(tixi.getArray(aeroPerformanceMapPath, 'cfz', aeroSize[1]))

    aeroPerformanceMap['cfx'] = aeroPerformanceMap['cfx'].reshape((len(Mach), len(Re), len(Beta), len(Alpha)))
    aeroPerformanceMap['cfy'] = aeroPerformanceMap['cfy'].reshape((len(Mach), len(Re), len(Beta), len(Alpha)))
    aeroPerformanceMap['cfz'] = aeroPerformanceMap['cfz'].reshape((len(Mach), len(Re), len(Beta), len(Alpha)))

    cfx = aeroPerformanceMap['cfx']
    cfy = aeroPerformanceMap['cfy']
    cfz = aeroPerformanceMap['cfz']

    #Transfrom cx and cz into app coordinate system (disregaring yaw)
    cd = np.zeros_like(cfx)
    cl = np.zeros_like(cfz)
    for i, aoa in enumerate(Alpha):
        cd[:, :, :, i] = cfx[:, :, :, i]*np.cos(np.deg2rad(aoa))+cfz[:, :, :, i]*np.sin(np.deg2rad(aoa))
        cl[:, :, :, i] = cfz[:, :, :, i]*np.cos(np.deg2rad(aoa))-cfx[:, :, :, i]*np.sin(np.deg2rad(aoa))
    aeroPerformanceMap['cd'] = cd
    aeroPerformanceMap['cl'] = cl

    aeroPerformanceMap['Sref'] = RefArea
    return aeroPerformanceMap

def getEngineCount(tixi):
    '''
    Helper Function to get the number of engines from an cpacs file.

    Parameters
    ----------
    tixi : tixiwrapper.Tixi
        instance of a Tixi object

    Returns
    -------
    int
        Number of engines
    '''
    Enginespath = '/cpacs/vehicles/aircraft/model/engines'
    nEnginesCPACS = tixi.getNamedChildrenCount(Enginespath, 'engine') #enginePositionType
    nEngine = 0
    for i in range(nEnginesCPACS):
        enginepath = Enginespath + getXPathChildString('/engine', i+1)
        if 'symmetry' in getAttributeNames(tixi, enginepath):
            nEngine += 2
        else:
            nEngine += 1
    return nEngine

def getEnginePerformanceMapDict(tixi, propulsionMapPath, idx_prop):
    '''
    Helper function to get the Propulsion Map data from a CPACS file

    Parameters
    ----------
    tixi : tixiwrapper.Tixi
        instance of a Tixi object
    propulsionMapPath : str
        path to the xml node of the aeroPerformanceMap, usually this is
        '/cpacs/vehicles/engines/engine/analysis/performanceMaps'
    idx_prop : int
        CPACS index of the performanceMaps/performanceMap

    Returns
    -------
    dict
        containing the propulsion data in 1D vector format
    '''
    ppath = propulsionMapPath + getXPathChildString('/performanceMap', idx_prop + 1)
    enginePerformanceMap = dict()
    enginePerformanceMap['machNumber'] = getVector(tixi, ppath + '/machNumber')
    enginePerformanceMap['flightLevel'] = getVector(tixi, ppath + '/flightLevel')
    enginePerformanceMap['thrust'] = getVector(tixi, ppath + '/thrust')
    enginePerformanceMap['mDotFuel'] = getVector(tixi, ppath + '/mDotFuel')
    return enginePerformanceMap

def copyCPACSPropulsionToAPP(enginePerformanceMap, jetThrust, jetFuel):
    '''
    Converts CPACS propulsion data into the APP format, and copies the data into
    a pyAPP6 JetPropulsion object.

    The APP fuel flow table is converted directely from the CPACS data. The Max.
    Thrust table is unique to APP and has to be created. This is done using the
    function PropulsionHelper.getMaxThrustTable. This function finds the maximum
    thrust values in the fuel flow data for each altitude and mach number and
    creates the new table.

    .. note::
        The min. thrust tabes of the APP data is left unchanged.

    Parameters
    ----------
    enginePerformanceMap : dict
        dictionary with propulsion data, as returned by pyAPP6Tools.CPACS.getEnginePerformanceMapDict()
    jetThrust : pyAPP6.JetThrust
        instance of a pyAPP6 JetThrust object
    jetFuel : pyAPP6.JetFuel
        instance of a pyAPP6 JetFuel object
    '''
    ffTable = jetFuel.fuelTable

    propAlt = enginePerformanceMap['flightLevel']
    propMach = enginePerformanceMap['machNumber']
    propT = enginePerformanceMap['thrust']
    propFF = enginePerformanceMap['mDotFuel']

    TableHelper.addArraysToX3Table(propAlt, propMach, propT, propFF, ffTable)

    PropulsionHelper.getMaxThrustFromFuelData(ffTable, jetThrust.maxThrustTable)

def copyCPACSAeroToAPP(aeroPerformanceMap, idx_re, aero, globalcd0=0.0):
    '''
    Converts CPACS drag data into the APP format.

    The missing table CLmax = f(Mach) is created from CL using max(CL)
    The CPACS drag polar CD is split into CD0 = f(M) and CDi=f(CL) by using CDi=min(CD) and
    CDi = CD - min(CD).

    Parameters
    ----------
    aeroPerformanceMap : dict
        dictionary with aerodynamic data, as returned by pyAPP6Tools.CPACS.getAerodynamicDict()
    idx_re : int
        CPACS index of the reynolds number. This will be subject to change in future CPACS files
    aero : pyAPP6.Files.Aero
        instance of the pyAPP6 Aero class where the CPACS data will be copied to
    globalcd0 : float
        optional additional global cd0 value
    '''

    Alpha = aeroPerformanceMap['angleOfAttack']
    Beta = aeroPerformanceMap['angleOfYaw']
    Mach = aeroPerformanceMap['machNumber']

    aero.Sref.xx = aeroPerformanceMap['Sref']

    #Check at which Position Beta equals zero:
    idx_beta0 = np.where(Beta == 0.0)[0][0]

    #Build CDI table, CL table and CLmax table
    aero.cdITable.clear()
    aero.clTable.clear()
    aero.cd0Table.clear()
    clmax = []
    cd0List = []

    for i, mach in enumerate(Mach):
        clAPP = aeroPerformanceMap['cl'][i, idx_re, idx_beta0, :]
        cdAPP = aeroPerformanceMap['cd'][i, idx_re, idx_beta0, :]
        cd0 = np.min(cdAPP)
        cdi_table = np.vstack([clAPP, cdAPP-cd0]).T
        aero.cdITable.insertTable(mach, cdi_table)

        cl_table = np.vstack([np.deg2rad(Alpha), clAPP]).T
        aero.clTable.insertTable(mach, cl_table)

        cd0List.append(cd0+globalcd0)
        clmax.append(np.max(clAPP))

    #insert Clmax and CD0 table
    aero.clmaxTable.table = np.vstack([Mach, clmax]).T
    aero.cd0Table.insertTable(0.0, np.vstack([Mach, cd0List]).T)
