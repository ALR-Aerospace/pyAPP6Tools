# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 09:35:53 2017

@author: alr
"""
#pylint: disable-msg=C0103

import os, sys
import numpy as np

from pyAPP6.Files import AircraftModel
from pyAPP6Tools import CPACS

sys.path.append(r'C:\Program Files\TIXI 2.2.4\share\tixi\python')
import tixiwrapper

def convertCPACStoAPP(cpacspath, outpath, overwrite=False):
    '''
    Example to convert a CPACS aircraft file to an APP6 aircraft file

    This example uses an existing, empty APP aircraft file (GenericJet.acft),
    that already defines a configuration. Therefore, to get a working APP aircraft,
    only the data tables for Mass&Limits, Aerodynamics and Propulsion have to
    be filled with correct data.
    '''

    acftPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'GenericJet.acft')
    acft = AircraftModel.fromFile(acftPath)
    aero = acft.getAero(0)
    engine = acft.getPropulsion(0)
    cfg = acft.getMassLimits(0)

    tixi = tixiwrapper.Tixi()
    tixi.openDocument(cpacspath)

    #Aerodynamics
    RefAreaPath = '/cpacs/vehicles/aircraft/model/reference/area'
    RefArea = tixi.getDoubleElement(RefAreaPath)
    aeroPerformanceMapPath = '/cpacs/vehicles/aircraft/model/analyses/aeroPerformanceMap'
    aeroPerformanceMap = CPACS.getAerodynamicDict(tixi, aeroPerformanceMapPath, RefArea)
    CPACS.copyCPACSAeroToAPP(aeroPerformanceMap, idx_re=0, aero=aero, globalcd0=0.0)

    #Propulsion
    propulsionMapPath = '/cpacs/vehicles/engines/engine/analysis/performanceMaps'
    enginePerformanceMap = CPACS.getEnginePerformanceMapDict(tixi, propulsionMapPath, 0)
    mThrust = engine.thrustData[0]
    mFuel = engine.fuelData[0]
    CPACS.copyCPACSPropulsionToAPP(enginePerformanceMap, mThrust, mFuel)

    #Mass&Limits
    AoAmin = np.deg2rad(-10.0)
    AoAmax = np.deg2rad(45.0)
    g_max = 9.0
    g_min = -2.0
    MmaxSL = 0.95 #Mach limiter (very simplified)
    copyMassLimitstoAPP(cfg, tixi, 0, AoAmin, AoAmax, g_min, g_max, MmaxSL)

    #optinally rename the Mass&Limits dataset. This name could be extracted from
    #CPCAS as well:
    name = 'Basline'
    #cpath = ''
    #name = tixi.getTextAttribute(cpath, 'uID')
    acft.configName[0] = name #rename configuration
    proj = acft.getConfiguration()
    proj.configName[0] = name #re-link configruation in project

    acft.saveToFile(outpath, overwrite=overwrite)


def copyMassLimitstoAPP(cfg, tixi, idx_opCase, AoAmin=-10.0, AoAmax=45.0, g_min=-2.0, g_max=9.0, MmaxSL=3.0):
    '''
    Find mass and limits data in APP. This needs a revision.
    '''
    Configpath = '/cpacs/vehicles/aircraft/model/analyses/weightAndBalance/operationalCases'
    fuelpath = '/cpacs/vehicles/aircraft/model/analyses/massBreakdown/fuel/massDescription/mass'

    cpath = Configpath + CPACS.getXPathChildString('/operationalCase', idx_opCase+1)

    cfg.mass.structure.xx = tixi.getDoubleElement(cpath+'/mass')
    cfg.mass.internalFuel.xx = tixi.getDoubleElement(fuelpath)

    #add number of engines:
    nEngine = CPACS.getEngineCount(tixi)
    cfg.nEngines.xx = float(nEngine) #Nr. of engines in APP is a float...

    #add limits:
    cfg.limitAoAMax.xx = AoAmax
    cfg.limitAoAMin.xx = AoAmin
    cfg.posLimitLF.xx = g_max
    cfg.negLimitLF.xx = g_min
    cfg.limitMachTable.table = np.array([[0.0, MmaxSL]])

if __name__ == "__main__":
    '''
    Example script to convert a CPACS xml file into an APP file.
    '''
    inputCPACSFile = r'D150_AGILE_Hangar.xml'
    outputAppFile = r'D150_AGILE_Hangar_converted.acft'
    convertCPACStoAPP(inputCPACSFile, outputAppFile, overwrite=True)
    print 'CPACS File converted.'
