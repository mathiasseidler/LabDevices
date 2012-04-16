'''
Created on 13.04.2012

@author: Mathias
'''
from enthought.traits.api import HasTraits, Event, Array, Str, Instance, Button
from enthought.traits.ui.api import View, Item, ButtonEditor, Action
from enthought.enable.api import Component, ComponentEditor
from threading import Thread


#my own classes 
from Devices.TranslationalStage_3Axes import TranslationalStage_3Axes
from Devices.Thorlabs_PM100D import Thorlabs_PM100D

import time
import numpy as np
from Mayavi import Mayavi

class FieldData(HasTraits):
    __slots__ = 'data'
    data = Array
    

        
class AcquireThread(Thread):
    PLUS = 1
    MINUS= -1
    def __init__(self,*args, **kw):
        super(AcquireThread, self).__init__(*args, **kw)
        #self.power_meter  = Thorlabs_PM100D("PM100D")
        #self.stage        = TranslationalStage_3Axes('COM3','COM4')   
    def run(self):
        self.threed_map_measurement()
    
    def threed_map_measurement(self):
        power_meter  = Thorlabs_PM100D("PM100D")
        stage        = TranslationalStage_3Axes('COM3','COM4')
        speed = 2
        self.model.data = np.array([[[]]])
        stage.AG_UC2_1.move_to_limit(1, -speed)
        stage.AG_UC2_1.move_to_limit(2, -speed)
        stage.AG_UC2_2.move_to_limit(1, -speed)
        
        for i in range(0,20):
            a_slice = np.array([])
            for j in range(0,10):
                row = np.array([])
                for k in range(0,10):
                    if self.wants_abort:
                        return
                    row = np.append(power_meter.getPower(),row)
                    stage.left(1)    
                a_slice = np.append(row, a_slice)         
                stage.up(1)
                stage.AG_UC2_1.move_to_limit(1,-speed)
            a_slice = np.resize(a_slice, (10,10))
            if i==0:
                self.model.data = np.append(self.model.data, a_slice)
                self.model.data = np.resize(a_slice,(10,10))
            else:
                print self.model.data.shape
                print a_slice.shape
                self.model.data = np.vstack((self.model.data, a_slice))    
            stage.backwards(1)
            stage.AG_UC2_2.move_to_limit(1, -speed)
            stage.AG_UC2_1.move_to_limit(1, -speed)
    
          
    def find_vertical_max(self):
        power_meter  = Thorlabs_PM100D("PM100D")
        stage        = TranslationalStage_3Axes('COM3','COM4')
        negative_slope = False
        a = np.array([])
        std = np.array([])
        treshold = 1e-5
        
        # this is just searching into the upwards direction
        for i in range(0,10):
            tmp = np.array([])
            tmp = np.append(tmp, power_meter.getPower())
            a = np.append(a, np.average(tmp))
            std= np.append(std,np.std(tmp))
        t = time.time()    
        while not negative_slope and (time.time()-t) < 60:
            tmp = np.array([])
            stage.AG_UC2_2.jog(1, 1)
            for i in range(0,10):
                tmp = np.append(tmp, power_meter.getPower())
            std = np.append(std,np.std(tmp))
            a = np.append(a, np.average(tmp))
            if a[-1]+std[-1] < a[-2] and a[-1] > treshold:
                negative_slope = True
        stage.AG_UC2_2.stop_jog(1)                     

        
        
class OpticalAxisMainGUI(HasTraits):
    '''
    classdocs
    '''
    # data
    data_model = Instance(FieldData,())
    
    # plot container
    plot_container = Instance(Component)
    plot_size=(600,400)
    plot_item = Item('plot_container',editor=ComponentEditor(size=plot_size),show_label=False)
    
    # Maya
    mayavi = Instance(Mayavi,())
    mayavi_item = Item('mayavi', style='custom')
    
    # acquire threads
    capture_thread=Instance(AcquireThread) 

    # Buttons
    thread_control = Event
    button_label_tc = Str('Start acquisition')
    button_tc = Item('thread_control' ,show_label=False, editor=ButtonEditor(label_value='button_label_tc'))
    
    # Status Fields
    status_field = Str("Welcome\n This is multiline\n\n")
    
    view = View(button_tc, 
                #plot_item,
                mayavi_item,
                Item('status_field', show_label=False, style='readonly'),
                resizable=True)
    
    def _thread_control_fired(self):
        if self.capture_thread and self.capture_thread.isAlive():
            self.capture_thread.wants_abort = True
        else:
            self.capture_thread=AcquireThread()
            self.capture_thread.wants_abort = False
            self.capture_thread.model = self.data_model
            self.capture_thread.gui = self
            self.capture_thread.start()
    
gui=OpticalAxisMainGUI()
gui.configure_traits()
        