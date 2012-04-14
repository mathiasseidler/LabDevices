'''
Created on 13.04.2012

@author: Mathias
'''
from enthought.traits.api import HasTraits, Event, Str, Instance, Button
from enthought.traits.ui.api import View, Item, ButtonEditor, Action
from threading import Thread


#my own classes 
from Devices.TranslationalStage_3Axes import TranslationalStage_3Axes
from Devices.Thorlabs_PM100D import Thorlabs_PM100D

class OpticalAxisData(HasTraits):
    z_data=None
    

        
class AcquireThread(Thread):
    
    def __init__(self,*args, **kw):
        super(AcquireThread, self).__init__(*args, **kw)
        self.power_meter  = Thorlabs_PM100D("PM100D")
        self.stage        = TranslationalStage_3Axes('COM3','COM4')   
    def run(self):
        
        
        
class OpticalAxisMainGUI(HasTraits):
    '''
    classdocs
    '''
    capture_thread=Instance(AcquireThread) 

    #Buttons
    thread_control = Event
    button_label_tc = Str('Start acquisition')
    button_tc = Item('thread_control' , label='', editor=ButtonEditor(label_value='button_label_tc'))
    
    status_field = Str("Welcome\n This is multiline")
    
    view = View(button_tc, 
                Item('status_field', show_label=False, style='readonly'))
    

    
gui=OpticalAxisMainGUI()
gui.configure_traits()
        