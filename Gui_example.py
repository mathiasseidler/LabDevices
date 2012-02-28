"""
This demo shows how Chaco and Traits
 can be used to easily build a data
acquisition and visualization system.
Two frames are opened: one has the plot and allows configuration of
various plot properties, and one which simulates controls for the hardware
device from which the data is being acquired; in this case, it is a mockup
random number generator whose mean and standard deviation can be controlled
by the user.

"""
# Major library imports
import random
import wx
from numpy import arange, array, hstack, random
# Enthought imports
from enthought.traits.api import Array, Bool, Callable, Enum, Float, HasTraits, \
                                 Instance, Int, Trait
from enthought.traits.ui.api import Group, HGroup, Item, View, spring, Handler
from enthought.pyface.timer.api import Timer
# Chaco imports
from enthought.chaco.chaco_plot_editor import ChacoPlotItem


class Viewer(HasTraits):
    """ This Class just contains the two data arrays that will be updated
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
                               x_label="Time",
                               y_label="Signal",
                               color="blue",
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
    
    
class Controller(HasTraits):
   
    # A reference to the plot viewer object
    viewer = Instance(Viewer)
   
    # Some parameters controller the random signal that will be generated
    distribution_type = Enum("normal", "lognormal")
    mean = Float(0.0)
    stddev = Float(1.0)
   
    # The max number of data points to accumulate and show in the plot
    max_num_points = Int(100)
   
    # The number of data points we have received; we need to keep track of
    # this in order to generate the correct x axis data series.
    num_ticks = Int(0)
   
    # private reference to the random number generator.  this syntax
    # just means that self._generator should be initialized to
    # random.normal, which is a random number function, and in the future
    # it can be set to any callable object.
    _generator = Trait(random.normal, Callable)
   
    view = View(Group('distribution_type', 
                      'mean', 
                      'stddev',
                      'max_num_points',
                      orientation="vertical"),
                      buttons=["OK", "Cancel"])
   
    def timer_tick(self, *args):
        """ Callback function that should get called based on a wx timer
        tick.  This will generate a new random datapoint and set it on
        the .data array of our viewer object.
        """
        # Generate a new number and increment the tick count
        new_val = self._generator(self.mean, self.stddev)
        self.num_ticks += 1
       
        # grab the existing data, truncate it, and append the new point.
        # This isn't the most efficient thing in the world but it works.
        cur_data = self.viewer.data
        new_data = hstack((cur_data[-self.max_num_points+1:], [new_val]))
        new_index = arange(self.num_ticks - len(new_data) + 1, self.num_ticks+0.01)
       
        self.viewer.index = new_index
        self.viewer.data = new_data
        return

    def _distribution_type_changed(self):
        # This listens for a change in the type of distribution to use.
        if self.distribution_type == "normal":
            self._generator = random.normal
        else:
            self._generator = random.lognormal
           
# wxApp used when this file is run from the command line.
class MyApp(wx.App):
   
    def OnInit(self, *args, **kw):
        viewer = Viewer()
        controller = Controller(viewer = viewer)
       
        # Pop up the windows for the two objects
        viewer.edit_traits()
        controller.edit_traits()
       
        # Set up the timer and start it up
        self.setup_timer(controller)
        return True
    def setup_timer(self, controller):
        # Create a new WX timer
        timerId = wx.NewId()
        self.timer = wx.Timer(self, timerId)
       
        # Register a callback with the timer event
        self.Bind(wx.EVT_TIMER, controller.timer_tick, id=timerId)
       
        # Start up the timer!  We have to tell it how many milliseconds
        # to wait between timer events.  For now we will hardcode it
        # to be 100 ms, so we get 10 points per second.
        self.timer.Start(100.0, wx.TIMER_CONTINUOUS)
        return
# This is called when this example is to be run in a standalone mode.
if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()   
# EOF
