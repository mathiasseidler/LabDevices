'''
Created on Feb 29, 2012

@author: Administrator
'''

from NEWPORT_AG_UC2 import NEWPORT_AG_UC2
from time import sleep

class TranslationalStage_3Axes:
    '''
    channels for controller1
    '''
    channel_xaxes=1
    channel_yaxes=2
    
    '''
    channels for controller 2
    '''
    channel_zaxes=1
    
    
    def __init__(self,port_1,port_2):
        self.AG_UC2_1 = NEWPORT_AG_UC2(port_1)
        sleep(0.1)
        self.AG_UC2_2 = NEWPORT_AG_UC2(port_2)
        
    def up(self,steps,step_amplitude):
        self.AG_UC2_2.RelativeMove(self.channel_zaxes, steps, step_amplitude)
        
    def down(self,steps,step_amplitude):
        self.AG_UC2_2.RelativeMove(self.channel_zaxes, -steps, step_amplitude)
        
    def forwards(self,steps,step_amplitude):
        self.AG_UC2_1.RelativeMove(self.channel_yaxes, -steps, step_amplitude)
        
    def backwards(self,steps,step_amplitude):
        self.AG_UC2_1.RelativeMove(self.channel_yaxes, steps, step_amplitude)
    
    def left(self,steps,step_amplitude):
        self.AG_UC2_1.RelativeMove(self.channel_xaxes, steps, step_amplitude)
    
    def right(self,steps,step_amplitude):
        self.AG_UC2_1.RelativeMove(self.channel_xaxes, -steps, step_amplitude)