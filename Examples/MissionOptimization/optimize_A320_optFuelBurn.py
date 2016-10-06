# -*- coding: utf-8 -*-
"""
Created on Tue Oct 04 15:49:07 2016

@author: alr
"""

from pyAPP6Tools import MissionOptimization
from pyAPP6Tools.MissionOptimization import segmentParameter, resFunctionMinimizeEndValue, missionObjective, updateEndCondition

if __name__ == "__main__":
    misfile = r'A320_optFuelBurn.mis'
    
    segParList = [segmentParameter(3,154.33,updateEndCondition),
                  segmentParameter(4,0.78,updateEndCondition),
                  segmentParameter(5,9144,updateEndCondition),
                  segmentParameter(7,154.33,updateEndCondition)]
    
    
    obj = missionObjective('Fuel Mass',resFunctionMinimizeEndValue,mode='max')
    
    res = MissionOptimization.optimizeMission(misfile=misfile, segParList=segParList, misObjective=obj)
