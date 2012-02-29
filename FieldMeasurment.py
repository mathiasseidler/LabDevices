'''
Created on 24.02.2012

@author: Mathias
'''
from enthought.traits.api import HasTraits, Str, Instance, Array,Button, Any, Enum
from enthought.traits.ui.api import View, VGroup, HGroup, Item, Controller, spring
from enthought.chaco.api import Plot, create_line_plot,LinePlot, \
                         add_default_grids, add_default_axes, ArrayPlotData
from enthought.enable.component_editor import ComponentEditor
from enthought.chaco.chaco_plot_editor import ChacoPlotItem

from threading import Thread
from FibreCoupling import TransStage
from Devices.Thorlabs_PM100D import Thorlabs_PM100D
from enthought.pyface.timer.api import Timer

import numpy as np
from enthought.pyface.timer.api import Timer

class FieldDataViewer(HasTraits):
    """ This class just contains the two data arrays that will be updated
    by the Controller.  The visualization/editor for this class is a
    Chaco plot.
    """ 
    index = Array  
    data = Array
    plot_type = Enum("line", "scatter")
   
    # This "view" attribute defines how an instance of this class will
    # be displayed when .edit_traits() is called on it.  (See MyApp.OnInit()
    # below.)
    view = View(ChacoPlotItem("index", "data",
                               type_trait="plot_type",
                               resizable=True,
                               x_label="Index",
                               y_label="Signal",
                               color="black",
                               bgcolor="white",
                               border_visible=True,
                               border_width=1,
                               padding_bg_color="lightgray",
                               width=800,
                               height=380,
                               show_label=False),
                HGroup(spring, Item("plot_type", style='custom'), spring),
                resizable = True,
                buttons = ["OK"],
                width=800, height=500)
    

#class AquireData(Thread):
class DAQThread(Thread):

    def run(self):
        powermeter  = Thorlabs_PM100D("PM100D")
        while not self.wants_abort:
            self.field_data.index = np.append(self.field_data.index, len(self.field_data.data)+1)
            self.field_data.data = np.append(self.field_data.data, float(powermeter.getPower()))
            import time
            time.sleep(0.2)
                  
     
class Controller(HasTraits):
   
    # A reference to the plot viewer object
    viewer = Instance(FieldDataViewer,())
    Start_Measurment=Button
    print_data=Button
    capture_thread=Instance(DAQThread)
    timer = Instance(Timer)
    thread=Any()
    view=View(Item('viewer', style='custom', show_label=False), 
              'Start_Measurment', 'print_data',
                resizable=True)
                  
    def _Start_Measurment_fired(self):
        #self.timer=Timer(100, self.timer_tick)
        #self.thread=Thread(target=self.timer_tick)
        #self.thread.start()
        if self.capture_thread and self.capture_thread.isAlive():
            self.capture_thread.wants_abort = True
        else:
            self.capture_thread = DAQThread()
            self.capture_thread.wants_abort = False
            self.capture_thread.field_data = self.viewer
            self.capture_thread.start()
            
    def _print_data_fired(self):
        print self.viewer.data
        print self.viewer.index
        
c = Controller()
c.configure_traits()
    
    
