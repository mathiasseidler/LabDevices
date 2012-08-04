'''
Created on Jul 11, 2012

@author: Administrator
'''
from Devices.Thorlabs_PM100D import Thorlabs_PM100D
if __name__ == '__main__':
    pm100d = Thorlabs_PM100D('PM100D')
    print pm100d.getPower()