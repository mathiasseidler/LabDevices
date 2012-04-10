
"""

"""

from enthought.traits.api import HasTraits, Str, Instance, Array, Button, Any, Enum, Int, Event,Trait, Callable
from enthought.traits.ui.api import View, VGroup, HGroup, Item, Controller, Group
from enthought.enable.api import BaseTool
from enthought.traits.api import on_trait_change
from enthought.traits.ui.editors import ButtonEditor
from enthought.chaco.default_colormaps import *
from enthought.traits.ui.menu import Action, CloseAction, Menu, MenuBar, OKCancelButtons, Separator
                 
from enthought.chaco.api import ArrayDataSource, ArrayPlotData, ColorBar, ContourLinePlot, \
                                 ColormappedScatterPlot, CMapImagePlot, \
                                 ContourPolyPlot, DataRange1D, VPlotContainer, \
                                 DataRange2D, GridMapper, GridDataSource, \
                                 HPlotContainer, ImageData, LinearMapper, \
                                 LinePlot, OverlayPlotContainer, Plot, PlotAxis
                                 
from enthought.enable.api import Window                        
                         
from enthought.enable.component_editor import ComponentEditor

from threading import Thread
from Devices.TranslationalStage_3Axes import TranslationalStage_3Axes
from Devices.Thorlabs_PM100D import Thorlabs_PM100D
from matplotlib import rc
from time import sleep

from enthought.traits.ui.menu import Action, CloseAction, Menu, \
                                     MenuBar, NoButtons, Separator

from numpy import array, linspace, meshgrid, nanmin, nanmax,  pi, zeros, ones, save, load, \
                append, hstack, vstack
from enthought.chaco.tools.api import LineInspector, PanTool, RangeSelection, \
                                   RangeSelectionOverlay, ZoomTool, DragZoom
                                   
from enthought.traits.api import File
from enthought.traits.ui.key_bindings import KeyBinding, KeyBindings

def append_left_oriented(matrix, row):
    diff = matrix.shape[1] - row.size
    if diff < 0:
        diff = -diff
        filling = zeros((matrix.shape[0],diff))
        matrix=hstack((matrix,filling))
    elif diff > 0:
        filling = zeros(diff)
        row = hstack((row,filling))
    matrix=vstack((matrix,row))
    return matrix

def append_right_oriented(matrix, row):
    diff = matrix.shape[1] - row.size
    if diff < 0:
        diff = -diff
        filling = zeros((matrix.shape[0],diff))
        matrix=hstack((filling,matrix))
    elif diff > 0:
        filling = zeros(diff)
        row = hstack((filling,row))
    matrix=vstack((matrix,row))
    return matrix


class FieldData(HasTraits):
    """ Data and Index of the field
    """  
    __slots__ = 'intensity_map','data', 'index'
    intensity_map = Array
    data = Array
    index = Array
    
class CaptureThread(Thread):
    def run(self):
        self.measure3()

    def measure1(self):
        print self
        try:
            power_meter  = Thorlabs_PM100D("PM100D")
            stage       = TranslationalStage_3Axes('COM3','COM4')   
        except:
            print "Exception raised: Devices not available"
            return
        self.fd.intensity_map = array([[]])
        i=0
        while not self.wants_abort and i<self.step_range: #needs to be improved
            row = array([])
            for k in range(1,5): #moving out of the limit
               row = append(row, power_meter.getPower())
               stage.left(self.steps, self.step_amplitude)  
            while stage.AG_UC2_1.get_limit_status() == 'PH0' and not self.wants_abort: #get one line moving to the left
                row = append( row, power_meter.getPower())
                stage.left(self.steps, self.step_amplitude)
            self.fd.intensity_map= append_left_oriented(self.fd.intensity_map, row)
            stage.backwards(self.steps, self.step_amplitude)
            
            row=array([])                   
            for k in range(1,5): #moving out of the limit
               row = append(power_meter.getPower(),row)
               stage.right(self.steps, self.step_amplitude)       
            while stage.AG_UC2_1.get_limit_status() == 'PH0' and not self.wants_abort:
                row = append(power_meter.getPower(), row)
                stage.right(self.steps, self.step_amplitude)
            self.fd.intensity_map = append_right_oriented(self.fd.intensity_map, row)        
            stage.backwards(self.steps, self.step_amplitude)
            i+=1
        print self.fd.intensity_map
        
    def measure2(self):
        try:
            power_meter  = Thorlabs_PM100D("PM100D")
            stage       = TranslationalStage_3Axes('COM3','COM4')   
        except:
            print "Exception raised: Devices not available"
            return
        
        self.fd.intensity_map=array([[]])
        row=array([[]])
        index = 100
        
        
        for i in range(0,index):
            for j in range(0,index):
                row = append(power_meter.getPower(),row)
                stage.left(self.steps, self.step_amplitude)
            self.fd.intensity_map = append_left_oriented(self.fd.intensity_map, row)
            stage.backwards(self.steps, self.step_amplitude)
            
            for j in range(0,index):
                row = append(power_meter.getPower(),row)
                stage.right(self.steps, self.step_amplitude)
            self.fd.intensity_map = append_right_oriented(self.fd.intensity_map, row)
            stage.backwards(self.steps, self.step_amplitude)
            print self.fd.intensity_map
            
    def measure3(self):
        try:
            power_meter  = Thorlabs_PM100D("PM100D")
            stage       = TranslationalStage_3Axes('COM3','COM4')   
        except:
            print "Exception raised: Devices not available"
            return
        
        self.fd.intensity_map=array([[]])
        #index = 10
        stage.AG_UC2_1.move_to_limit(1, -3)
        for i in range(0,self.step_range):
            row=array([])
            for j in range(0,150):
                if self.wants_abort:
                    return
                row = append(power_meter.getPower(),row)
                stage.left(self.steps, self.step_amplitude)
                
            if i==0:
                self.fd.intensity_map = append(self.fd.intensity_map, row)
            else:
                self.fd.intensity_map = vstack((self.fd.intensity_map, row))
                
            stage.backwards(self.steps, 50)#self.step_amplitude)
            stage.AG_UC2_1.move_to_limit(1, -3)
        
class CustomTool(BaseTool): 
    #right click
    def normal_right_down(self, event):
        '''
        on right click
        '''
        print event
            
            
class FieldDataController(HasTraits):
    
    model=Instance(FieldData)
    
    plot=Instance(Plot,())
    plot_data=Instance(ArrayPlotData)
    renderer = Any()
    
    step_amplitude = Int(16)
    step_range = Int(100)
    steps = Int(5)
    
    thread_control = Event
    capture_thread=Instance(CaptureThread) 
    label_button_measurment = Str('Start acquisition')
    
    _save_file = File('default.npy', filter=['Numpy files (*.npy)| *.npy'])
    _load_file = File('.npy',  filter=['Numpy files (*.npy) | *.npy', 'All files (*.*) | *.*'])
    # Define the view associated with this controller:
    view = View(Item('thread_control' , label="Acquisition", editor = ButtonEditor(label_value = 'label_button_measurment')),
                'step_amplitude', 'step_range', 'steps',
                Item('plot',editor=ComponentEditor(),show_label=False),
                menubar=MenuBar(Menu(Action(name="load data", action="load_file"), # action= ... calls the function, given in the string
                                     Action(name="save data", action="save_file"), 
                        Separator(),
                        CloseAction,
                        name="File")),
                #key_bindings = key_bindings,
                resizable=True)
    
    save_file_view = View(Item('_save_file'), 
                          buttons=OKCancelButtons, 
                          kind='livemodal',  # NB must use livemodal, plot objects don't copy well
                          width=400,
                          resizable=True)
    load_file_view = View(Item('_load_file'), 
                          buttons=OKCancelButtons, 
                          kind='livemodal',  # NB must use livemodal, plot objects don't copy well
                          width=400,
                          resizable=True)  
    
    def __init__(self,*args, **kw):
        super(FieldDataController, self).__init__(*args, **kw)
        #self.plotdata = ArrayPlotData(x = self.model.index, y = self.model.data)

        self.model.intensity_map = array([[]])

        # Create a plot data obect and give it this data
        self.plot_data = ArrayPlotData()
        self.plot_data.set_data("imagedata", self.model.intensity_map)
        # Create a contour polygon plot of the data
        plot = Plot(self.plot_data, default_origin="top left")
        plot.bgcolor = 'gray'
        plot.img_plot("imagedata",
                             name='my_plot', 
                            # xbounds=x,
                             #ybounds=y,
                             colormap=jet,
                             hide_grids=True)[0]
        self.plot = plot
        
    def _thread_control_fired(self):
        # if not self.running:
        if self.capture_thread and self.capture_thread.isAlive():
            self.capture_thread.wants_abort = True
            self.label_button_measurment = 'Start acquisition'
        else:
            self.capture_thread = CaptureThread()
            self.capture_thread.wants_abort = False
            self.capture_thread.fd = self.model
            self.capture_thread.plotdata= self.plot_data
            self.capture_thread.step_amplitude = self.step_amplitude
            self.capture_thread.start()
            self.capture_thread.step_range = self.step_range
            self.capture_thread.steps = self.steps
            self.label_button_measurment = 'Stop acquisition'
            #import time
            #time.sleep(0.1)
            
    def _step_amplitude_changed(self):
        if self.capture_thread:
            self.capture_thread.stepamplitude = self.step_amplitude
            
    @on_trait_change('model.intensity_map')        
    def updatePlot(self,name,old,new):
        if self.plot_data and new.ndim > 1:
            print 'update Plot'
            #print 'update plot'
            #print self.model.intensity_map
            self.plot_data.set_data("imagedata", new)
            # Create a contour polygon plot of the data
            plot = Plot(self.plot_data, default_origin="top left")
            plot.bgcolor = 'gray'
            plot.img_plot("imagedata",
                             name='my_plot', 
                            # xbounds=x,
                             #ybounds=y,
                             colormap=jet,
                             hide_grids=True)[0]
            self.plot = plot
            self.plot.request_redraw()

    def save_file(self):
        """
        Callback for the 'Save Image' menu option.
        """
        ui = self.edit_traits(view='save_file_view')
        if ui.result == True:
            save(self._save_file, self.model.intensity_map)
            
    def load_file(self):
        """
        Callback for the 'Load Image' menu option.
        """
        ui = self.edit_traits(view='load_file_view')
        if ui.result == True:
            try:
                self.model.intensity_map = load(self._load_file)
            except:
                print 'Loading the file failed'
            
        
    
ui = FieldDataController(model=FieldData(index=array([]),data=array([]), intensity_map=array([[0][0]])))
ui.configure_traits(view='view')
