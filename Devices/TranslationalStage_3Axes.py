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
        sleep(0.1)
        
    def up(self,steps):
        self.AG_UC2_2.relative_move(self.channel_zaxes, steps)
        
    def down(self,steps):
        self.AG_UC2_2.relative_move(self.channel_zaxes, -steps)
        
    def forwards(self,steps):
        self.AG_UC2_1.relative_move(self.channel_yaxes, -steps)
        
    def backwards(self,steps):
        self.AG_UC2_1.relative_move(self.channel_yaxes, steps)
    
    def left(self,steps):
        self.AG_UC2_1.relative_move(self.channel_xaxes, steps)
    
    def right(self,steps):
        self.AG_UC2_1.relative_move(self.channel_xaxes, -steps)