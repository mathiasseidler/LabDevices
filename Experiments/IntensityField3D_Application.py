'''
Created on 07.05.2012

@author: Mathias
'''


from enthought.traits.api import HasTraits, Event, Array, Str, Int, Instance, Button, on_trait_change
from enthought.traits.ui.api import View, Item, ButtonEditor, Action, Tabbed, Group, HGroup, VGroup
from enthought.enable.api import Component, ComponentEditor
from threading import Thread


from enthought.chaco.api import ArrayDataSource, BarPlot, DataRange1D, \
        LinearMapper, VPlotContainer, PlotAxis, FilledLinePlot, \
        add_default_grids, PlotLabel, add_default_axes, HPlotContainer



#my own classes 
from Devices.TranslationalStage_3Axes import TranslationalStage_3Axes
from Devices.Thorlabs_PM100D import Thorlabs_PM100D
from ScalarField3DPlot import ScalarField3DPlot_GUI
from HandyClasses.IntensityFieldStageController import find_vertical_max, find_horizontal_max


import time
import numpy as np

class StageConfiguration(HasTraits):
    steps_backwards = Int(100)
    steps_side = Int(20)
    steps_up = Int(60)
    steps_per_move = Int(5)
    step_amplitude_side = Int(16)
    step_amplitude_up=Int(25)
    step_amplitude_backwards=Int(50)
    
    group_config = HGroup(VGroup('steps_backwards','steps_side','steps_up','steps_per_move'),
                          VGroup('step_amplitude_backwards','step_amplitude_side','step_amplitude_up'))
    view = View(group_config)
    
class Data(HasTraits):
    field3d = Array    

class DAQThread(Thread):
    def __init__(self,*args, **kw):
        super(DAQThread, self).__init__(*args, **kw)
 
    def run(self):
        self.threed_map_measurement()   
    
    def threed_map_measurement(self):
        power_meter  = Thorlabs_PM100D("PM100D")
        stage        = TranslationalStage_3Axes('COM3','COM4')
        speed = 2

        stage.AG_UC2_1.move_to_limit(1, -speed)
        stage.AG_UC2_1.move_to_limit(2, -speed)
        stage.AG_UC2_2.move_to_limit(1, -speed)
        
        stage.AG_UC2_1.set_step_amplitude(1, self.stage_config.step_amplitude_side)
        stage.AG_UC2_1.set_step_amplitude(1, -self.stage_config.step_amplitude_side)
        stage.AG_UC2_1.set_step_amplitude(2, self.stage_config.step_amplitude_backwards)
        stage.AG_UC2_1.set_step_amplitude(2, -self.stage_config.step_amplitude_backwards)
        stage.AG_UC2_2.set_step_amplitude(1, self.stage_config.step_amplitude_up)
        stage.AG_UC2_2.set_step_amplitude(1, -self.stage_config.step_amplitude_up)       
        
        for i in range(0,self.stage_config.steps_backwards): # looping to acquire slices vertical slices
            a_slice = np.array([])
            for j in range(0, self.stage_config.steps_up): # looping through the rows
                row = np.array([])
                for k in range(0, self.stage_config.steps_side):
                    if self.wants_abort:
                        return
                    row = np.append(power_meter.getPower(),row)
                    stage.left(self.stage_config.steps_per_move)    
                a_slice = np.append(row, a_slice)         
                stage.up(self.stage_config.steps_per_move)
                stage.AG_UC2_1.move_to_limit(1,-speed)
            a_slice = np.resize(a_slice, (30,25))
            if i==0:
                self.model.field3d = np.append(self.model.field3d, a_slice)
            else:
                print self.model.field3d.shape
                print a_slice.shape
                self.model.field3d = np.vstack((self.model.field3d, a_slice))    
            stage.backwards(self.stage_config.steps_per_move)
            stage.AG_UC2_2.move_to_limit(1, -speed)
            stage.AG_UC2_1.move_to_limit(1, -speed)


class IntensityField3D_GUI(HasTraits):
    data = Instance(Data,())
    mayavi = Instance(ScalarField3DPlot_GUI,())
    stage_config = Instance(StageConfiguration,())
    capture_thread = Instance(DAQThread)
    thread_control = Event
    label_button_thread = Str('Start acquisition')
    
    # preparing the gui itself
    item_mayavi = Item('mayavi', show_label = False, style='custom')
    item_thread = Item('thread_control' , show_label=False, editor = ButtonEditor(label_value = 'label_button_thread'))  
    item_stage_config = Item('stage_config', show_label = False, style='custom')
    
    size = (800,600)
    view = View(item_stage_config, item_thread, item_mayavi, width=size[0], height=size[1], resizable=True) 
    
    def _thread_control_fired(self):
        self.data.field3d = np.array([[[]]])
        self.mayavi.set_data(self.data)
        # if not self.running:
        if self.capture_thread and self.capture_thread.isAlive():
            self.capture_thread.wants_abort = True
            self.label_button_thread = 'Start acquisition'
        else:
            self.capture_thread = DAQThread()
            self.capture_thread.wants_abort = False
            self.capture_thread.model = self.data
            self.capture_thread.stage_config = self.stage_config
            self.capture_thread.start()
            self.label_button_thread = 'Stop acquisition'
    
if __name__ == '__main__':
    gui=IntensityField3D_GUI()
    gui.configure_traits()