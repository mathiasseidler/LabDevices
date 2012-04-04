'''
Created on Feb 14, 2012

@author: Mathias, Jonathan
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
        try:
            self.port = port
            self.instr=visa.Instrument(self.port)
            print self.instr.ask('*idn?').strip()
        except:
            print 'Unexpected error: ', sys.exc_info()[0]
              
    def __del__(self):
        '''
        Destructor
        '''
        try:
            self.instr.close()
            print('PM100D' + '@Port:' + self.port + ' connection closed')
        except:
            print 'Unexpected error: ', sys.exc_info()[0]  
        
    def getPower(self):
        '''
        return: 
            Power in Watt
        '''
        self.instr.write('pow:unit W')
        self.instr.write('conf:pow')
        return float(self.instr.ask("read?"))
    
    def set_wavelength(self, length):
        '''
        Sets the wavelength correction of the power meter to parameter "length".
        '''
        if type(length) is int or type(length) is float or type(length) is long:
            if 400 < length < 1100:
                self.instr.write("CORR:WAV length")
            else:
                print 'Error: specified wavelength must be between 400 and 1100 nm'
    
        