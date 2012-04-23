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
        add_default_grids, PlotLabel, add_default_axes, HPlotContainer



#my own classes 
from Devices.TranslationalStage_3Axes import TranslationalStage_3Axes
from Devices.Thorlabs_PM100D import Thorlabs_PM100D
from ScalarField3DPlot import ScalarField3DPlot_GUI
from HandyClasses.IntensityFieldStageController import find_vertical_max, find_horizontal_max


import time
import numpy as np


class FieldData(HasTraits):
    __slots__ = 'data', 'height', 'horizontal_pos', 'power_data'
    power_data = Array
    height = Array
    horizontal_pos = Array
    data = Array
    

        
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
        stage.AG_UC2_1.set_step_amplitude(1, 16)
        stage.AG_UC2_1.set_step_amplitude(2, 50)
        stage.AG_UC2_2.set_step_amplitude(1, 16)
        self.model.power_data = np.array([])
        std = np.array([])
        self.model.height =  np.array([])
        self.model.horizontal_pos = np.array([])
        
        # initial vertical positioning
        relative_height, mean, stdev = find_vertical_max(power_meter, stage, 1e-5)
        self.model.power_data = np.append(self.model.power_data, mean)
        std= np.append(std,stdev)
        self.model.height = np.append(self.model.height, relative_height)
        
        # initial horizontal positioning
        stage.AG_UC2_1.move_to_limit(1, -2)
        relative_horizontal, mean, stdev = find_horizontal_max(power_meter, stage, 1e-5)
        self.model.horizontal_pos = np.append(self.model.horizontal_pos, relative_horizontal)
        
        # move along the maximum in the field
        while self.wants_abort == False:
            #if self.wants_abort == True:
            #    break
            relative_height, mean, stdev = find_vertical_max(power_meter, stage, 1e-5)
            self.model.height = np.append(self.model.height, relative_height + self.model.height[0])
            
            relative_horizontal, mean, stdev = find_horizontal_max(power_meter, stage, 1e-5)            
            self.model.horizontal_pos = np.append(self.model.horizontal_pos, 
                                                  relative_horizontal+self.model.horizontal_pos[0])
            
            self.model.power_data = np.append(self.model.power_data, mean)
            std= np.append(std,stdev)         
            stage.backwards(1)
    
    def threed_map_measurement(self):
        power_meter  = Thorlabs_PM100D("PM100D")
        stage        = TranslationalStage_3Axes('COM3','COM4')
        speed = 2
        self.model.data = np.array([[[]]])
        stage.AG_UC2_1.move_to_limit(1, -speed)
        stage.AG_UC2_1.move_to_limit(2, -speed)
        stage.AG_UC2_2.move_to_limit(1, -speed)
        stage.AG_UC2_1.set_step_amplitude(3, 22)
        stage.AG_UC2_1.set_step_amplitude(2, 50)
        stage.AG_UC2_2.set_step_amplitude(1, 25)
        
        for i in range(0,200):
            a_slice = np.array([])
            for j in range(0,30):
                row = np.array([])
                for k in range(0,25):
                    if self.wants_abort:
                        return
                    row = np.append(power_meter.getPower(),row)
                    stage.left(1)    
                a_slice = np.append(row, a_slice)         
                stage.up(1)
                stage.AG_UC2_1.move_to_limit(1,-speed)
            a_slice = np.resize(a_slice, (30,25))
            if i==0:
                self.model.data = np.append(self.model.data, a_slice)
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
    horizontal_pos_ds = Instance(ArrayDataSource)
    horizontal_index_ds = Instance(ArrayDataSource)
    int_val_ds = Instance(ArrayDataSource)
    int_index_ds = Instance(ArrayDataSource)
    
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
                width=800,
                resizable=True)
    
    def _thread_control_fired(self):
        if self.capture_thread and self.capture_thread.isAlive():
            self.capture_thread.wants_abort = True
            self.button_label_tc = 'Start acquisition'
        else:
            self.capture_thread=AcquireThread()
            self.capture_thread.wants_abort = False
            self.capture_thread.model = self.data_model
            self.capture_thread.gui = self
            self.capture_thread.start()
            self.button_label_tc = 'Stop acquisition'
            
    def _plot_container_default(self):
        index = np.arange(100)
        value = 100.0 * index
        self.value_ds = ArrayDataSource(value)
        self.index_ds = ArrayDataSource(index)
        self.horizontal_pos_ds = ArrayDataSource(10 * index)
        self.horizontal_index_ds = ArrayDataSource(index)
        self.int_index_ds = ArrayDataSource(index)
        self.int_val_ds = ArrayDataSource(index*1000)
        return create_plot(self.value_ds, self.index_ds, self.horizontal_pos_ds, self.horizontal_index_ds,
                           self.int_val_ds, self.int_index_ds)
    
    @on_trait_change('data_model.height')        
    def update_plot(self,name,old,new):
        numpoints = new.size
        index = np.arange(numpoints)
        self.index_ds.set_data(index)
        self.value_ds.set_data(new)
        
    @on_trait_change('data_model.horizontal_pos')
    def update_horizontal_pos_plot(self, name, old, new):
        numpoints = new.size
        self.horizontal_index_ds.set_data(np.arange(numpoints))
        self.horizontal_pos_ds.set_data(new)
        
    @on_trait_change('data_model.power_data')
    def update_power_data_plot(self,name, old, new):
        numpoints = new.size
        self.int_index_ds.set_data(np.arange(numpoints))
        self.int_val_ds.set_data(new)      

def create_plot(value_ds, index_ds, horizontal_val_ds, horizontal_index_ds, int_val_ds, int_index_ds):
    xmapper = LinearMapper(range=DataRange1D(index_ds))
    value_mapper = LinearMapper(range=DataRange1D(value_ds))
    
    xmapper_val = LinearMapper(range=DataRange1D(horizontal_index_ds))
    horizontal_val_mapper =  LinearMapper(range=DataRange1D(horizontal_val_ds))
    
    int_xmapper = LinearMapper(range=DataRange1D(int_index_ds))
    int_val_mapper = LinearMapper(range=DataRange1D(int_val_ds))
    
    value_plot = FilledLinePlot(index = index_ds, value = value_ds,
                                index_mapper = xmapper,
                                value_mapper = value_mapper,
                                line_color = "black",
                                render_style='connectedhold',
                                fill_color = (0,0,1,0.3),
                                antialias=False)
    add_default_grids(value_plot)
    value_plot.overlays.append(PlotAxis(value_plot, orientation='left'))
    value_plot.overlays.append(PlotAxis(value_plot, orientation='bottom'))
    value_plot.overlays.append(PlotLabel('position of max power: vertical axes', component=value_plot, font = 'swiss 16', overlay_position='top'))

    
    value_plot.padding = 50
    

    horizontal_pos_plot = FilledLinePlot(index = horizontal_index_ds, value = horizontal_val_ds,
                                index_mapper = xmapper_val,
                                value_mapper = horizontal_val_mapper,
                                line_color = "black",
                                render_style='connectedhold',
                                fill_color = (0,1,0,0.3),
                                antialias=False)
    
    horizontal_pos_plot.padding = 50
    add_default_grids(horizontal_pos_plot)
    horizontal_pos_plot.overlays.append(PlotAxis(horizontal_pos_plot, orientation='left'))
    horizontal_pos_plot.overlays.append(PlotAxis(horizontal_pos_plot, orientation='bottom'))
    horizontal_pos_plot.overlays.append(PlotLabel('position of max power: horizontal axes', component=horizontal_pos_plot, font = 'swiss 16', overlay_position='top'))
    
    intensity_plot = FilledLinePlot(index = int_index_ds, value = int_val_ds,
                            index_mapper = int_xmapper,
                            value_mapper = int_val_mapper,
                            line_color = "black",
                            fill_color = (0,0,0,0.4),
                            antialias=False)
    intensity_plot.padding = 50
    add_default_grids(intensity_plot)
    intensity_plot.overlays.append(PlotAxis(intensity_plot, orientation='left'))
    intensity_plot.overlays.append(PlotAxis(intensity_plot, orientation='bottom'))
    intensity_plot.x_axis.tick_label_formatter = lambda x: ('%.0f'%(x*1e6))
    intensity_plot.overlays.append(PlotLabel('Power of transmitted beam', component=intensity_plot, font = 'swiss 16', overlay_position='top'))
    
    
    container = VPlotContainer(use_backbuffer = True)
    container.add(horizontal_pos_plot)
    container.add(value_plot)
    #container.add(intensity_plot)
    container_h = HPlotContainer(use_backbuffer = True)
    container_h.add(container)
    container_h.add(intensity_plot)
    return container_h 

gui=OpticalAxisMainGUI()
gui.configure_traits()
        