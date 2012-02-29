'''
Created on Feb 29, 2012

@author: Administrator
'''

from NEWPORT_AG_UC2 import NEWPORT_AG_UC2

class TranslationalStage_3Axes:
    '''
    channels for controller1
    '''
    channel_xaxes=2
    channel_yaxes=1
    
    channel_zaxes=1
    
    
    def __init__(self,port_1,port_2):
        self.AG_UC2_1 = NEWPORT_AG_UC2(port_1)
        self.AG_UC2_2 = NEWPORT_AG_UC2(port_2)
        
    def up(self,steps,stepamplitude):
        self.RelativeMove(self.vertical_channel, steps, stepamplitude)
        
    def down(self,steps,stepamplitude):
        self.RelativeMove(self.vertical_channel, -steps, stepamplitude)
        
    def forwards(self,steps,stepamplitude):
        self.RelativeMove(self.horizontal_channel, -steps, stepamplitude)
        
    def backwards(self,steps,stepamplitude):
        self.RelativeMove(self.horizontal_channel, steps, stepamplitude)
    
    def left(self,steps,step_amplitude):
        pass
    
    def right(self,steps,step_ampliutde):
        pass