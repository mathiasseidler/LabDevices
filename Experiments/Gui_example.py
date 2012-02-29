
"""

"""
# Imports:
from enthought.traits.api import HasTraits, Str, Instance, Array, Button, Any, Enum, Int, Event
from enthought.traits.ui.api import View, VGroup, HGroup, Item, Controller
from enthought.traits.ui.editors import ButtonEditor
from enthought.chaco.api import Plot, create_line_plot,LinePlot, \
                         add_default_grids, add_default_axes, ArrayPlotData, jet
from enthought.enable.component_editor import ComponentEditor
from enthought.chaco.chaco_plot_editor import ChacoPlotItem
from enthought.chaco.tools.api import PanTool, ZoomTool, DragZoom

import threading
from threading import Thread
from FibreCoupling import TransStage
from Devices.Thorlabs_PM100D import Thorlabs_PM100D
from enthought.pyface.timer.api import Timer
from matplotlib import rc
import numpy as np

class FieldData ( HasTraits ):
    """ Data and Index of the field
    """  
    # A name:
    intensity_map = Array
    data = Array
    index = Array

class CaptureThread(Thread):
    def run(self):
        try:
            power_meter  = Thorlabs_PM100D("PM100D")
            stage       = TransStage('COM3')   
        except:
            print "Devices not available"
            
        while not self.wants_abort:
                #data_power[i]=powermeter.getPower()
            stage.backwards(1, self.stepamplitude)
            import time
            time.sleep(0.1)
            self.fd.index = np.append(self.fd.index,len(self.fd.data)+1)
            self.fd.data = np.append(self.fd.data,power_meter.getPower()*10E7)
            self.plotdata.set_data('x',self.fd.index)
            self.plotdata.set_data('y', self.fd.data)
            
            #print "length index: " + str(len(self.fd.index)) + "length data: " + str(len(self.fd.data)) 
            #print  'Index: ' + str(self.fd.index)+ 'Data: ' + str(self.fd.data)



class FieldDataController(Controller):
    """ Define a combined controller/view class that validates that
        MyModel.name is consistent with the 'allow_empty_string' flag.
    """
    model=Instance(FieldData)
    plot=Instance(Plot,())
    capture_thread=Instance(CaptureThread) 
    plot_data=Instance(ArrayPlotData)
    timer = Instance(Timer)
    renderer = Any()
    step_amplitude = Int(1)
    
    thread_control = Event
    label_button_measurment = Str('Start acquisition')

    # Define the view associated with this controller:
    view = View(Item('controller.thread_control' , label="Acquisition", editor = ButtonEditor(label_value = 'label_button_measurment')),
                'controller.step_amplitude',
                Item('controller.plot',editor=ComponentEditor(),show_label=False),
                resizable=True)
    
    def __init__(self,*args, **kw):
        super(FieldDataController, self).__init__(*args, **kw)
        #self.plotdata = ArrayPlotData(x = self.model.index, y = self.model.data)

        xs = np.linspace(-2*np.pi, 2*np.pi, 600)
        ys = np.linspace(-1.5*np.pi, 1.5*np.pi, 300)
        x, y = np.meshgrid(xs,ys)
        z = np.tanh(x*y/6)*np.cosh(np.exp(-y**2)*x/3)
        self.model.intensity_map = x*y
        # Create a plot data obect and give it this data
        self.plot_data = ArrayPlotData()
        self.plot_data.set_data("imagedata", self.model.intensity_map)
        # Create a contour polygon plot of the data
        plot = Plot(self.plot_data, default_origin="top left")
        plot.contour_plot("imagedata", 
                          type="poly",
                          poly_cmap=jet,
                          xbounds=(xs[0], xs[-1]), 
                          ybounds=(ys[0], ys[-1]),
                          name='Intensity map')
        # Create a contour line plot for the data, too
        plot.contour_plot("imagedata", 
                          type="line",
                          xbounds=(xs[0], xs[-1]), 
                          ybounds=(ys[0], ys[-1]))
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
            self.capture_thread.plotdata= self.plotdata
            self.capture_thread.stepamplitude = self.step_amplitude
            self.capture_thread.start()
            self.label_button_measurment = 'Stop acquisition'
            #import time
            #time.sleep(0.1)
            
    def _step_amplitude_changed(self):
        if self.capture_thread:
            self.capture_thread.stepamplitude = self.step_amplitude
        
    
ui = FieldDataController(FieldData(index=np.array([]),data=np.array([]), intensity_map=np.array([[0][0]])))
ui.configure_traits()
    
