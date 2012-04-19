'''
Created on 13.04.2012

@author: Mathias
'''
from enthought.traits.api import HasTraits, Event, Array, Str, Instance, Button, on_trait_change
from enthought.traits.ui.api import View, Item, ButtonEditor, Action
from enthought.enable.api import Component, ComponentEditor
from threading import Thread


from enthought.chaco.api import ArrayDataSource, BarPlot, DataRange1D, \
        LinearMapper, VPlotContainer, PlotAxis, FilledLinePlot, \
        add_default_grids, PlotLabel, add_default_axes



#my own classes 
from Devices.TranslationalStage_3Axes import TranslationalStage_3Axes
from Devices.Thorlabs_PM100D import Thorlabs_PM100D
from ScalarField3DPlot import ScalarField3DPlot_GUI
from HandyClasses.IntensityFieldStageController import find_vertical_max


import time
import numpy as np


class FieldData(HasTraits):
    __slots__ = 'data', 'height'
    data = Array
    height = Array
    

        
class AcquireThread(Thread):
    def __init__(self,*args, **kw):
        super(AcquireThread, self).__init__(*args, **kw)
        #self.power_meter  = Thorlabs_PM100D("PM100D")
        #self.stage        = TranslationalStage_3Axes('COM3','COM4')   
    def run(self):
        self.along_maxium()
    
    def along_maxium(self):
        power_meter  = Thorlabs_PM100D("PM100D")
        stage        = TranslationalStage_3Axes('COM3','COM4')
        stage.AG_UC2_2.move_to_limit(1,-2)
        a = np.array([])
        std = np.array([])
        height = np.array([])
        self.model.height = height
        for i in xrange(0,20):
            h, mean, stdev = find_vertical_max(power_meter, stage, 1e-5)
            a = np.append(a, mean)
            std= np.append(std,stdev)
            height = np.append(height, h)
            stage.backwards(1)
    
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
    
    # data sources for the plot
    index_ds = Instance(ArrayDataSource)
    value_ds = Instance(ArrayDataSource)
    
    
    # Maya
    mayavi = Instance(ScalarField3DPlot_GUI,())
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
                plot_item,
                #mayavi_item,
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
            
    def _plot_container_default(self):
        index = np.arange(100)
        value = 100.0 * index
        self.value_ds = ArrayDataSource(value)
        self.index_ds = ArrayDataSource(index)
        return create_plot(self.value_ds, self.index_ds)
    
    @on_trait_change('data_model.height')        
    def update_plot(self,name,old,new):
        self.value_ds.set_data(new)
        numpoints = self.value_ds.get_size()
        index = np.arange(numpoints)
        self.index_ds.set_value(index)

def create_plot(value_ds, index_ds):
    xmapper = LinearMapper(range=DataRange1D(index_ds))
    value_mapper = LinearMapper(range=DataRange1D(value_ds))
    
    value_plot = FilledLinePlot(index = index_ds, value = value_ds,
                                index_mapper = xmapper,
                                value_mapper = value_mapper,
                                edge_color = "black",
                                face_color = (0,0,1,0.4),
                                bgcolor = "white",
                                border_visible = True)
    add_default_grids(value_plot)
    #add_default_axes(value_plot)
    value_plot.overlays.append(PlotAxis(value_plot, orientation='left'))
    value_plot.overlays.append(PlotAxis(value_plot, orientation='bottom'))
    value_plot.padding = 30
    return value_plot    

gui=OpticalAxisMainGUI()
gui.configure_traits()
        