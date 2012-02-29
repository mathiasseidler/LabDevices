
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

import threading
from threading import Thread
from FibreCoupling import TransStage
from LabDevices.Thorlabs_PM100D import Thorlabs_PM100D
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
    plotdata=Instance(ArrayPlotData)
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
        self.plotdata = ArrayPlotData()
        self.plotdata.set_data("imagedata", self.model.intensity_map)
        plot = Plot(self.plotdata)
        plot.contour_plot('imagedata',type='poly',name='Intensity map',poly_cmap=jet)
        plot.x_axis.title = 'Index'
        plot.y_axis.title = r'Power [$\mu$W]'
        self.renderer = plot.plot(("x", "y"), type="line", color="black")
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
        
    
ui = FieldDataController(FieldData(index=np.array([]),data=np.array([])))
ui.configure_traits()
    
