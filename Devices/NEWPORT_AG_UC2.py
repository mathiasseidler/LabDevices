'''
Created on Feb 13, 2012

@author: Mathias

'''

import visa
import time
import sys
from LabDeviceExceptions import DeviceBusyError
from LabDeviceExceptions import Error

class NEWPORT_AG_UC2(object):
    '''
    This class implements functionality of the NewPort AG-UC2 Controller. 
    This device controls 2 NewPort AG-LS25 Translational Stages
    
    I wrote this class to use of the comfort of invoking class methods, instead of sending directly serial messages
    to the controller. 
    I hope this adds overview, of what I'm doing  
    Plus I can add functionality for experiments.
    
    PyVisa is used to send Serial commands to the device. 
    
    14.2.2012 Raising exception in case of mistakes is implemented in some functions
    13.2.2012 implementing the different serial function calls
    '''


    def __init__(self,port):
        '''
        Constructor
        '''
        try:
            self.port = port
            self.device = visa.SerialInstrument(self.port, baud_rate=921600)
            print self.device.ask('VE').strip()
            self.setToRemoteControl()

        except:
            print 'Unexpected error: ', sys.exc_info()[0]
          
          
    def __del__(self):
        try:
            self.setToLocalMode()
            self.device.close()
            print('AG-UC2' + '@Port:' + self.port + ' connection closed.')
        except:
            print 'Unexpected error: ', sys.exc_info()[0]         
             
    def RelativeMove(self, AxisNumber,NumberOfSteps,StepAmplitude):
        '''
        Moves the chosen stage relatively to current position by the distance of NumberOfSteps * StepAmplitude
        Unfortunately it is hard do find out what's the absolute measure of one step.  I'm working on it.
        
        StepAmplitude:
            Between -50 and +50
            Sets the step amplitude (step size) in positive or negative direction. 
            If the parameter is positive, it will set the step amplitude in the forward direction. 
            If the parameter is negative, it will set the step amplitude in the backward direction.
        
        NOTE:
            The step amplitude is a relative measure. The step amplitude corresponds to the amplitude of the electrical signal sent to the Agilis motor. 
            There is no linear correlation between the step amplitude and the effective motion size. 
            In particular, too low a setting for the step amplitude may result in no output motion. 
            Also, the same step amplitude setting for forward and backward direction may result in different size motion steps. 
            Also, the motion step size corresponding to a step amplitude setting may vary by position, load, and throughout the life time of the product. 
            The step amplitude setting is not stored after power down. The default value after power-up is 16.
        '''
        self.device.write(str(AxisNumber) + 'SU' + str(StepAmplitude) )
        self.device.write(str(AxisNumber)+'PR'+str(NumberOfSteps))
        self.waitUntilMovementDone()    
        self.CheckForErrorOfPreviousCommand()
        
    def MoveToMiddlePosition(self):   
        '''
        Move both stages into the middle position
        This command takes a while. It measures first the step number between the limits and
        is moving to he half of the max steps.
        '''             
        if self.device.ask('1TS') != '\n1TS0' or self.device.ask('2TS') != '\n2TS0':
            raise DeviceBusyError('One or both of the stages seem to be busy')
        # move axis 1 to middle position
        self.device.write('1PA500')
        time.sleep(1)     
        self.waitUntilMovementDone()
        # move axis 2 to middle position 
        self.device.write('2PA500')
        time.sleep(1)
        self.waitUntilMovementDone()    
    
    def StopMotion(self,AxisNumber):
        '''
        Stops the motion of the input axis
        
        Attribute:
            AxisNumber - the axis where the movement should be stoped
        Return:
            The Error code
        '''
        self.device.write(str(AxisNumber)+'ST')
        self.CheckForErrorOfPreviousCommand()
        
        
    def get_axis_status(self,AxisNumber):
        '''
        Returns the axis status
        '''
        return self.device.ask(str(AxisNumber)+'TS').strip()
    def get_limit_status(self):
        '''
        Returns the status of the limits
        Possible return messages:
        PH0: No limit switch is active
        PH1: Limit switch of channel #1 is active, limit switch of channel #2 is not active
        PH2: Limit switch of channel #2 is active, limit switch of channel #1 is not active
        PH3: Limit switch of channel #1 and channel #2 are active
        '''
        return self.device.ask('PH').strip()
    
    def CheckForErrorOfPreviousCommand(self):
        '''
        Checks if the previous command was executed without error
        '''
        error_code=(self.device.ask('TE')).strip().strip('TE')
        if error_code != '0':
            raise PreviousCommandError(error_code)
       
    def setToRemoteControl(self):
        '''
        Necessary that the controller listens to the computer and not to the manual input
        '''
        self.device.write('MR') 
        self.CheckForErrorOfPreviousCommand()
        
    def setToLocalMode(self):
        '''
        Set Controller to local(manual) mode
        '''
        self.device.write('ML')
        self.CheckForErrorOfPreviousCommand()
        
    def waitUntilMovementDone(self):
        while self.device.ask('2TS') != '\n2TS0' or self.device.ask('1TS') != '\n1TS0':
            time.sleep(0.1)
        
class PreviousCommandError(Error):
    """
    Exception raised when the previous command returned an error          
    Attributes:
        msg  -- explanation of the error      
    """
    dictErrorCode={
          '-1':"Unknown Command",
          '-2':'Axis out of range(must be 1 or 2, or must be not specified)',
          '-3':'Wrong format for parameter nn (or must not be specified)',
          '-4':'Parameter nn out of range',
          '-5':'Not allowed in local mode',
          '-6':'Not allowed in current state'
    }
    
    def __init__(self, ErrorCode):
        print("error code: " + ErrorCode + ", error message: " + self.dictErrorCode.get(ErrorCode))
        self.msg=self.dictErrorCode.get(ErrorCode)