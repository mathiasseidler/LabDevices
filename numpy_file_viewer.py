#!/usr/bin/env python
"""
Draws a colormapped image plot
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom
   history".
"""
# Major library imports
from numpy import exp, linspace, meshgrid, pi, sin, load, save
from enthought.enable.example_support import DemoFrame, demo_main
# Enthought library imports
from enthought.enable.api import Component, ComponentEditor, Window
from enthought.traits.api import HasTraits, Instance, File, Str
from enthought.traits.ui.api import Item, Group, View
# Chaco imports
from enthought.chaco.api import ArrayPlotData, jet, Plot
from enthought.chaco.tools.api import PanTool, ZoomTool
from enthought.chaco.tools.api import TraitsTool
from enthought.chaco.tools.api import SaveTool
from enthought.traits.ui.menu import Action, CloseAction, Menu, \
                                     MenuBar, NoButtons, Separator
#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component(file_name):
    # Create a scalar field to colormap
    print(file_name)
    z = load(file_name)
    #xs = linspace(0, 10, 600)
    #ys = linspace(0, 5, 600)
    #x, y = meshgrid(xs,ys)
    # Create a plot data obect and give it this data
    pd = ArrayPlotData()
    pd.set_data("imagedata", z)
    # Create the plot
    plot = Plot(pd)

    img_plot = plot.img_plot("imagedata", 
                            # xbounds=x,
                             #ybounds=y,
                             colormap=jet)[0]
    # Tweak some of the plot properties
    plot.title = file_name
    plot.padding = 50
    # Attach some tools to the plot
    plot.tools.append(PanTool(plot))
    plot.tools.append(TraitsTool(plot))
    zoom = ZoomTool(component=img_plot, tool_mode="box", always_on=False)
    img_plot.overlays.append(zoom)
    plot.tools.append(SaveTool(plot))
    return plot
#===============================================================================
# Attributes to use for the plot view.
size=(800,600)
title="Basic Colormapped Image Plot"       
#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)
    file_name=Str('50sa.npy')
    _save_file = File('default.npy', filter=['Numpy files (*.npy)| *.npy'])
    _load_file = File('.npy',  filter=['Numpy files (*.npy) | *.npy', 'All files (*.*) | *.*'])   
   
    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size), show_label=False),orientation = "vertical"),
                        menubar=MenuBar(Menu(Action(name="Load File", action="load_file"), # action= ... calls the function, given in the string
                        Separator(),
                        CloseAction,
                        name="File")),
                    resizable=True, title=title
                    )
    def _plot_default(self):
        return _create_plot_component(self.file_name)
     
    def load_file(self):
        """
        Callback for the 'Load Image' menu option.
        """
        import easygui
        self.file_name = easygui.fileopenbox()
        if self.file_name:
            try:
                self.plot=self._plot_default()
            except:
                print 'Loading the file failed'
   
demo = Demo()
demo.configure_traits(view='traits_view')
#===============================================================================
# Stand-alone frame to display the plot.
#===============================================================================
#===============================================================================
# class PlotFrame(DemoFrame):
#    def _create_window(self):
#        # Return a window containing our plot
#        return Window(self, -1, component=_create_plot_component())       
# if __name__ == "__main__":
#    demo_main(PlotFrame, size=size, title=title)
#===============================================================================
