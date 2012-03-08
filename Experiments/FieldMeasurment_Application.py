
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

from numpy import array, linspace, meshgrid, nanmin, nanmax,  pi, zeros, ones, save, load

from enthought.chaco.tools.api import LineInspector, PanTool, RangeSelection, \
                                   RangeSelectionOverlay, ZoomTool, DragZoom
                                   
from enthought.traits.api import File
from enthought.traits.ui.key_bindings import KeyBinding, KeyBindings


class FieldData(HasTraits):
    """ Data and Index of the field
    """  
    __slots__ = 'intensity_map','data', 'index'
    intensity_map = Array
    data = Array
    index = Array

class CaptureThread(Thread):
    def run(self):
        try:
            power_meter  = Thorlabs_PM100D("PM100D")
            stage       = TranslationalStage_3Axes('COM3','COM4')   
        except:
            print "Exception raised: Devices not available"
            return
        i = 0
        while i < 100 and not self.wants_abort:
            for j in xrange(0,100):
                self.fd.intensity_map[i,j] = power_meter.getPower()
                stage.left(1, self.step_amplitude)
            stage.up(1,self.step_amplitude)
            i+=1
            for j in xrange(99,-1,-1):
                self.fd.intensity_map[i,j] = power_meter.getPower()
                stage.right(1,self.step_amplitude)
            #stage.up(1,self.step_amplitude)
            stage.forwards(1, self.step_amplitude)
        print self.fd.intensity_map

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
    
    thread_control = Event
    capture_thread=Instance(CaptureThread) 
    label_button_measurment = Str('Start acquisition')
    
    _save_file = File('default.npy', filter=['Numpy files (*.npy)| *.npy'])
    _load_file = File('.npy',  filter=['Numpy files (*.npy) | *.npy', 'All files (*.*) | *.*'])
    # Define the view associated with this controller:
    view = View(Item('thread_control' , label="Acquisition", editor = ButtonEditor(label_value = 'label_button_measurment')),
                'step_amplitude',
                Item('plot',editor=ComponentEditor(),show_label=False),
                menubar=MenuBar(
                   Menu(Action(name="Load Plot", action="load"),
                        Action(name="Save Plot", action="save"), 
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

        self.model.intensity_map = zeros((100,100))

        # Create a plot data obect and give it this data
        self.plot_data = ArrayPlotData()
        self.plot_data.set_data("imagedata", self.model.intensity_map)
        # Create a contour polygon plot of the data
        plot = Plot(self.plot_data, default_origin="top left")
        plot.contour_plot("imagedata", 
                          type="poly",
                          poly_cmap=jet,
                          name='Intensity map')
        # Create a contour line plot for the data, too
        plot.contour_plot("imagedata", 
                          type="line")
        # Tweak some of the plot properties
        plot.title = "Intensity Map"
        plot.padding = 50
        plot.bg_color = "black"
        plot.fill_padding = True 
        # Attach some tools to the plot
        plot.tools.append(PanTool(plot))
        zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)
            
        dragzoom = DragZoom(plot, drag_button="right")
        plot.tools.append(dragzoom)
        plot.tools.append(CustomTool(plot))
        #plot.x_axis.title = 'Index'
        #plot.y_axis.title = r'Power [$\mu$W]'
        #self.renderer = plot.plot(("x", "y"), type="line", color="black")
        self.plot = plot     
        #add_default_grids(self.plot)
        #add_default_axes(self.plot)
        
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
            self.label_button_measurment = 'Stop acquisition'
            #import time
            #time.sleep(0.1)
            
    def _step_amplitude_changed(self):
        if self.capture_thread:
            self.capture_thread.stepamplitude = self.step_amplitude
            
    @on_trait_change('model.intensity_map')        
    def updatePlot(self,name,old,new):
        if self.plot_data:
            self.plot_data.set_data('imagedata',self.model.intensity_map)

    def save(self):
        """
        Callback for the 'Save Image' menu option.
        """
        ui = self.edit_traits(view='save_file_view')
        if ui.result == True:
            save(self._save_file, self.model.intensity_map)
            
    def load(self):
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
