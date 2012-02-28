'''
Created on Feb 13, 2012

@author: Mathias
'''

class Error(Exception):
    '''
    classdocs
    '''
    pass
    
    

class DeviceBusyError(Error):
    '''
    Exception raised when the Device is busy and can't process the request  
          
    Attributes:
        msg  -- explanation of the error
        
    '''
    def __init__(self, msg):
        self.msg = msg
        
    
        
        
    
    
        