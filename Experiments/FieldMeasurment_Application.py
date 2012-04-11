
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
                                 LinePlot, OverlayPlotContainer, Plot, PlotAxis, ImageData
                                 
from enthought.enable.api import Window                        
                         
from enthought.enable.api import ComponentEditor, Component

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
from pylab import unravel_index

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
    intens_vert = Array
    data = Array
    index = Array
    
class CaptureThread(Thread):
    def run(self):
        self.measure3()
            
    def measure3(self):
        try:
            power_meter  = Thorlabs_PM100D("PM100D")
            stage       = TranslationalStage_3Axes('COM3','COM4')   
        except:
            print "Exception raised: Devices not available"
            return
        
        self.fd.intensity_map=array([[]])
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
            
        #acquire vertical plane   
        stage.AG_UC2_1.move_to_limit(2,-3)
        max_index=unravel_index(self.fd.intensity_map.argmax(), self.fd.intensity_map.shape)
        stage.backwards(max_index[0], self.step_amplitude)
        stage.AG_UC2_2.move_to_limit(1,-2) # check for direction
        self.fd.int_vert = array([[]])
        
        for i in range(0,self.step_range):
            row=array([])
            for j in range(0,150):
                if self.wants_abort:
                    return
                row = append(power_meter.getPower(),row)
                stage.left(self.steps, self.step_amplitude)
            if i==0:
                self.fd.intensity_map = append(self.fd.int_vert, row)
            else:
                self.fd.intensity_map = vstack((self.fd.int_vert, row))    
            stage.up(self.steps, 50)#self.step_amplitude)
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
    
    plot_container=Instance(Component)
    plot_data=Instance(ArrayPlotData)
    _image_value = Instance(ImageData)
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
                Item('plot_container',editor=ComponentEditor(),show_label=False),
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
        self.model.intens_vert = array([[]])
        # Create a plot data obect and give it this data
        self.create_plot_component()
        
    def create_plot_component(self):
        self.plot_data = ArrayPlotData()
        self.plot_data.set_data("imagedata", self.model.intensity_map)
        self.plot_data.set_data('vert_image',self.model.intens_vert)
        # Create a contour polygon plot of the data
        self.plot = Plot(self.plot_data, default_origin="top left")
        self.plot.bgcolor = 'gray'
        self.plot.padding=5
        self.plot.padding_left=25
        self.plot.padding_bottom=20
        self.plot.img_plot("imagedata", name='my_plot', # xbounds=x,#ybounds=y,
                             colormap=jet, hide_grids=True)[0]
                             
        self.rplot = Plot(self.plot_data)
        self.rplot.padding=self.plot.padding
        self.rplot.padding_left=self.plot.padding_left
        self.rplot.padding_bottom=self.plot.padding_bottom   
        self.rplot.img_plot('vert_image',name='vert_plot',colormap=jet,bgclor='gray')
          
        container = HPlotContainer(use_backbuffer = True)
        container.add(self.plot)
        container.add(self.rplot)
        self.plot_container = container
            
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
            self.plot_data.set_data('imagedata',new)
            self.plot.delplot('my_plot')
            self.plot.img_plot("imagedata", name='my_plot', # xbounds=x,#ybounds=y,
                             colormap=jet, hide_grids=True)[0]
            self.plot.invalidate_and_redraw()

    def save_file(self):
        """
        Callback for the 'Save Image' menu option.
        """
        ui = self.edit_traits(view='save_file_view')
        if ui.result == True:
            save(self._save_file, self.model.intensity_map)
            save(self._save_file + '_vertical',self.model.intens_vert)
            
    def load_file(self):
        """
        Callback for the 'Load Image' menu option.
        """
        import easygui
        tmp = easygui.fileopenbox(title = "Choose your file",default="*.npy")
        #ui = self.edit_traits(view='load_file_view')
        if tmp:
            self._load_file=tmp
            try:
                self.model.intensity_map = load(self._load_file)
            except:
                print 'Loading the file failed'
            
        
    
ui = FieldDataController(model=FieldData(index=array([]),data=array([]), intensity_map=array([[0][0]])))
ui.configure_traits(view='view')
