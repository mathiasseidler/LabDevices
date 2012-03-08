'''
Created on Feb 14, 2012

@author: Mathias
'''
import visa

class Thorlabs_PM100D:
    '''
    This class enables communication with the Thorlabs power meter 100D, via SCPI-Commands
    PyVisa is used for sending the commands
    '''

    def __init__(self,port):
        '''
        Constructor
        '''
        print 'Thorlabs PM100D constructor'
        self.device=visa.Instrument(port)
        
    def getPower(self):
        self.device.write('conf:pow')
        return self.device.ask("read?")
        