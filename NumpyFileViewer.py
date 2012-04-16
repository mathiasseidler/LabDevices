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
from enthought.chaco.api import ArrayPlotData, jet, Plot, ColorBar, HPlotContainer, LinearMapper
from enthought.chaco.tools.api import PanTool, ZoomTool
from enthought.chaco.tools.api import TraitsTool
from enthought.chaco.tools import toolbars
from enthought.chaco.tools.api import SaveTool, RangeSelection, RangeSelectionOverlay
from enthought.traits.ui.menu import Action, CloseAction, Menu, \
                                     MenuBar, NoButtons, Separator
from enthought.chaco.scales.formatters import BasicFormatter
from enthought.chaco.tools.image_inspector_tool import ImageInspectorTool, ImageInspectorOverlay

                    
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
    plot.bgcolor = 'gray'
    
    img_plot = plot.img_plot("imagedata",
                             name='my_plot', 
                            # xbounds=x,
                             #ybounds=y,
                             colormap=jet,
                             hide_grids=True)[0]
    cont_plot=plot.contour_plot('imagedata', type='line', name='countour')
    # Tweak some of the plot properties
    plot.title = file_name
    plot.padding = 40
    plot.padding_right=20
    # Attach some tools to the plot
    plot.tools.append(PanTool(plot))
    #plot.tools.append(TraitsTool(plot))
    zoom = ZoomTool(component=img_plot, tool_mode="box", always_on=False)
    img_plot.overlays.append(zoom)
    #plot.y_axis.tick_label_formatter = lambda x: "%.3e" % x
    #plot.x_axis.tick_label_formatter = lambda x: "%.3e" % x
    #plot.tools.append(SaveTool(plot))
    # Right now, some of the tools are a little invasive, and we need the
    # actual CMapImage object to give to them
    my_plot = img_plot#plot.plots["my_plot"][0]
    colormap = my_plot.color_mapper
    colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                        color_mapper=colormap,
                        plot=my_plot,
                        orientation='v',
                        resizable='v',
                        width=25,
                        padding=0)
    colorbar.origin = 'bottom left'
    #colorbar._axis.tick_label_formatter = lambda x: '%.0e'%(x*10e6) + u' [\u00b5' + 'Watt]'
    colorbar._axis.tick_label_formatter = lambda x: ('%.0f'%(x*1e6))
    colorbar._axis.orientation = 'right'
    colorbar._axis.title = u'Intensity [\u00b5W]'
    colorbar.padding_top = plot.padding_top
    colorbar.padding_bottom = plot.padding_bottom
    colorbar.padding_right = 100
    # create a range selection for the colorbar
    range_selection = RangeSelection(component=colorbar)
    colorbar.tools.append(range_selection)
    colorbar.overlays.append(RangeSelectionOverlay(component=colorbar,
                                                   border_color="white",
                                                   alpha=0.5,
                                                   fill_color="lightgray"))
    
    range_selection.listeners.append(my_plot)
    
    imgtool = ImageInspectorTool(img_plot)
    img_plot.tools.append(imgtool)
    plot.overlays.append(ImageInspectorOverlay(component=img_plot, image_inspector=imgtool))
    # we also want to the range selection to inform the cmap plot of
    # the selection, so set that up as well

    # Create a container to position the plot and the colorbar side-by-side
    container = HPlotContainer(use_backbuffer = True)
    container.add(plot)
    container.add(colorbar)
    container.bgcolor = "white"
    container.tools.append(SaveTool(container))
    container.tools.append(TraitsTool(container))
    #my_plot.set_value_selection((-1.3, 6.9))
    return container    
#===============================================================================
# Attributes to use for the plot view.
size=(800,600)
title="Basic Colormapped Image Plot"   
#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)
    file_name=Str('measure_3.npy')
    _save_file = File('default.npy', filter=['Numpy files (*.npy)| *.npy'])
    _load_file = File('.npy',  filter=['Numpy files (*.npy) | *.npy', 'All files (*.*) | *.*'])   
   
    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size), show_label=False),orientation = "vertical"),
                        menubar=MenuBar(Menu(Separator(),Action(name="Load numpy-data", action="load_file"), # action= ... calls the function, given in the string
                                             Separator(),
                                             CloseAction,
                                             name="File")),
                    resizable=True, title=title
                    )
    def _plot_default(self):
        try:
            return _create_plot_component(self.file_name)
        except:
            print 'some mistakes happened'
     
    def load_file(self):
        """
        Callback for the 'Load Image' menu option.
        """
        import easygui
        self.file_name = easygui.fileopenbox()
        print self.file_name
        if self.file_name:
            try:
                self.plot=self._plot_default()
            except:
                print 'Loading file failed'
   
demo = Demo()
demo.configure_traits(view='traits_view')
