# -*- coding: utf-8 -*-
"""
Created on Tue Oct 04 15:49:07 2016

@author: alr
"""

from pyAPP6Tools import MissionOptimization
from pyAPP6Tools.MissionOptimization import segmentParameter, resFunctionMinimizeEndValue, missionObjective, updateEndCondition, updateClimbAngle
from pyAPP6 import Units

if __name__ == "__main__":
    misfile = r'RutowskiClimb.mis'
    
    segParList = [segmentParameter(0,11000.0,updateEndCondition),
                  segmentParameter(1,1.25,updateEndCondition),
                  segmentParameter(1,-1.0/Units._DEG,updateClimbAngle),
                  segmentParameter(2,1.0/Units._DEG,updateClimbAngle)]
    
    
    obj = missionObjective('Time', resFunctionMinimizeEndValue, mode='min')
    
    res = MissionOptimization.optimizeMission(misfile=misfile, segParList=segParList, misObjective=obj)
