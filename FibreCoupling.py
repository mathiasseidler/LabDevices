'''
Created on Feb 15, 2012

@author: Mathias Seidler
'''

from Devices.Thorlabs_PM100D import Thorlabs_PM100D
from Devices.NEWPORT_AG_UC2 import NEWPORT_AG_UC2
from Devices.LabDeviceExceptions import Error

import numpy as np


class TransStage(NEWPORT_AG_UC2):
    vertical_channel=2
    horizontal_channel=1
    def up(self,steps,stepamplitude):
        self.RelativeMove(self.vertical_channel, steps, stepamplitude)
        
    def down(self,steps,stepamplitude):
        self.RelativeMove(self.vertical_channel, -steps, stepamplitude)
        
    def forwards(self,steps,stepamplitude):
        self.RelativeMove(self.horizontal_channel, -steps, stepamplitude)
        
    def backwards(self,steps,stepamplitude):
        self.RelativeMove(self.horizontal_channel, steps, stepamplitude)


#powermeter  = Thorlabs_PM100D("PM100D")
#stage       = TransStage('COM3')


def measureUp():
    stepamplitude=3
    data_power=np.zeros(1000)
    for i in np.arange(0,999):
        data_power[i]=powermeter.getPower()
        stage.up(1, stepamplitude)
        
    plt.plot(data_power)
    plt.show()
    
    #get the index of the maximal power. so we know how many steps to move back to get to the position
    max_index=np.argmax(data_power)
    stage.down(1000-(max_index+1), stepamplitude)   #max_index+1 because of the indexing which starts at 0



