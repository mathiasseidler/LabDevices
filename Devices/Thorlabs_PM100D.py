'''
Created on Feb 14, 2012

@author: Mathias
'''
import visa
import sys

class Thorlabs_PM100D:
    '''
    This class enables communication with the Thorlabs power meter 100D, via SCPI-Commands
    PyVisa is used for sending the commands
    '''

    def __init__(self,port):
        '''
        Constructor
        '''
        self.port = port
        self.device=visa.Instrument(self.port)
        print self.device.ask('*idn?').strip()
        
    def __del__(self):
        try:
            self.device.close()
            print('PM100D connection closed')
        except:
            print 'Unexpected error: ', sys.exc_info()[0]  
        
    def getPower(self):
        self.device.write('conf:pow')
        return float(self.device.ask("read?"))
        