
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
    print diff
    if diff < 0:
        diff = -diff
        filling = zeros((matrix.shape[0],diff))
        matrix=hstack((matrix,filling))
    elif diff > 0:
        filling = zeros(diff)
        row = hstack((row,filling))
    matrix=vstack((row,matrix))
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
    matrix=vstack((row,matrix))
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
        try:
            power_meter  = Thorlabs_PM100D("PM100D")
            stage       = TranslationalStage_3Axes('COM3','COM4')   
        except:
            print "Exception raised: Devices not available"
            return
        self.fd = array([[]])
        while not self.wants_abort: #needs to be improved
            row = array([])
            while stage.AG_UC2_1.get_limit_status() == 'PH0': #get one line moving to the left
                row = append( row, power_meter.getPower())
                stage.left(1, self.step_amplitude)
            self.fd= append_left_oriented(self.fd, row)
            stage.forwards(1, self.step_amplitude)
            #===================================================================
            # for k in range(1,100): #moving out of the limit
            #    row = append(power_meter.getPower(),row)
            #    stage.right(1, self.step_amplitude)
            #===================================================================
            row=array([])               
            while stage.AG_UC2_1.get_limit_status() == 'PH0':
                row = append(power_meter.getPower(), row)
                stage.right(1, self.step_amplitude)
            self.fd = append_right_oriented(self.fd, row)        
            stage.forwards(1, self.step_amplitude)
        print self.fd.intensity_map

class CustomTool(BaseTool): 
    #right click
    def normal_right_down(self, event):
        '''
        on right click
        '''
        print event
        
    
class PlotUI(HasTraits):
    #Traits view definitions:
    traits_view = View(
        Group(Item('container',
                   editor=ComponentEditor(size=(800,600)),
                   show_label=False)),
        buttons=NoButtons,
        resizable=True)
    plot_edit_view = View(
        Group(Item('num_levels'),
              Item('colormap')),
              buttons=["OK","Cancel"])
    num_levels = Int(15)
    colormap = Enum(color_map_name_dict.keys())
    #---------------------------------------------------------------------------
    # Private Traits
    #---------------------------------------------------------------------------
   
    _image_index = Instance(GridDataSource)
    _image_value = Instance(ImageData)
    _cmap = Trait(jet, Callable)
    #---------------------------------------------------------------------------
    # Public View interface
    #---------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(PlotUI, self).__init__(*args, **kwargs)
        self.create_plot()
    def create_plot(self):
        # Create the mapper, etc
        self._image_index = GridDataSource(array([]), array([]), sort_order=("ascending","ascending"))
        image_index_range = DataRange2D(self._image_index)
        self._image_index.on_trait_change(self._metadata_changed, "metadata_changed")
       
        self._image_value = ImageData(data=array([]), value_depth=1)
        image_value_range = DataRange1D(self._image_value)
        
        # Create the contour plots
        self.polyplot = ContourPolyPlot(index=self._image_index, 
                                        value=self._image_value, 
                                        index_mapper=GridMapper(range=image_index_range), 
                                        color_mapper=self._cmap(image_value_range),
                                        levels=self.num_levels)
        
        self.lineplot = ContourLinePlot(index=self._image_index, 
                                        value=self._image_value, 
                                        index_mapper=GridMapper(range=self.polyplot.index_mapper.range),
                                        levels=self.num_levels)
        # Add a left axis to the plot
        left = PlotAxis(orientation='left',
                        title= "y",
                        mapper=self.polyplot.index_mapper._ymapper,
                        component=self.polyplot)
        self.polyplot.overlays.append(left)
   
        # Add a bottom axis to the plot
        bottom = PlotAxis(orientation='bottom',
                          title= "x",
                          mapper=self.polyplot.index_mapper._xmapper,
                          component=self.polyplot)
        self.polyplot.overlays.append(bottom)
        # Add some tools to the plot
        self.polyplot.tools.append(PanTool(self.polyplot, 
                                           constrain_key="shift"))
        self.polyplot.overlays.append(ZoomTool(component=self.polyplot, 
                                            tool_mode="box", always_on=False))
        self.polyplot.overlays.append(LineInspector(component=self.polyplot, 
                                               axis='index_x',
                                               inspect_mode="indexed",
                                               write_metadata=True,
                                               is_listener=False, 
                                               color="white"))
        self.polyplot.overlays.append(LineInspector(component=self.polyplot, 
                                               axis='index_y',
                                               inspect_mode="indexed",
                                               write_metadata=True,
                                               color="white",
                                               is_listener=False))
       
        # Add these two plots to one container
        contour_container = OverlayPlotContainer(padding=20,
                                                 use_backbuffer=True, 
                                                 unified_draw=True)
        contour_container.add(self.polyplot)
        contour_container.add(self.lineplot)
        # Create a colorbar
        cbar_index_mapper = LinearMapper(range=image_value_range)
        self.colorbar = ColorBar(index_mapper=cbar_index_mapper,
                                 plot=self.polyplot,
                                 padding_top=self.polyplot.padding_top,
                                 padding_bottom=self.polyplot.padding_bottom,
                                 padding_right=40,
                                 resizable='v',
                                 width=30)
        self.pd = ArrayPlotData(line_index = array([]),
                                line_value = array([]),
                                scatter_index = array([]),
                                scatter_value = array([]),
                                scatter_color = array([]))
        self.cross_plot = Plot(self.pd, resizable="h")
        self.cross_plot.height = 100
        self.cross_plot.padding = 20
        self.cross_plot.plot(("line_index", "line_value"), 
                             line_style="dot")
        self.cross_plot.plot(("scatter_index","scatter_value","scatter_color"),
                             type="cmap_scatter",
                             name="dot",
                             color_mapper=self._cmap(image_value_range),
                             marker="circle", 
                             marker_size=8)
        self.cross_plot.index_range = self.polyplot.index_range.x_range
        self.pd.set_data("line_index2", array([])) 
        self.pd.set_data("line_value2", array([])) 
        self.pd.set_data("scatter_index2", array([])) 
        self.pd.set_data("scatter_value2", array([])) 
        self.pd.set_data("scatter_color2", array([])) 
        self.cross_plot2 = Plot(self.pd, width = 140, orientation="v", resizable="v", padding=20, padding_bottom=160)
        self.cross_plot2.plot(("line_index2", "line_value2"), 
                             line_style="dot")
        self.cross_plot2.plot(("scatter_index2","scatter_value2","scatter_color2"),
                             type="cmap_scatter",
                             name="dot",
                             color_mapper=self._cmap(image_value_range),
                             marker="circle", 
                             marker_size=8)
        self.cross_plot2.index_range = self.polyplot.index_range.y_range
       
        # Create a container and add components
        self.container = HPlotContainer(padding=40, fill_padding=True,
                                        bgcolor = "white", use_backbuffer=False)
        inner_cont = VPlotContainer(padding=0, use_backbuffer=True)
        inner_cont.add(self.cross_plot)
        inner_cont.add(contour_container)
        self.container.add(self.colorbar)
        self.container.add(inner_cont)
        self.container.add(self.cross_plot2)
    def update(self, model):
        self.minz = model.minz
        self.maxz = model.maxz
        self.colorbar.index_mapper.range.low = self.minz
        self.colorbar.index_mapper.range.high = self.maxz
        self._image_index.set_data(model.xs, model.ys)
        self._image_value.data = model.zs
        self.pd.set_data("line_index", model.xs)
        self.pd.set_data("line_index2", model.ys)
        self.container.invalidate_draw()
        self.container.request_redraw()
  
    #---------------------------------------------------------------------------
    # Event handlers
    #---------------------------------------------------------------------------
    def _metadata_changed(self, old, new):
        """ This function takes out a cross section from the image data, based
        on the line inspector selections, and updates the line and scatter
        plots."""
       
        self.cross_plot.value_range.low = self.minz
        self.cross_plot.value_range.high = self.maxz
        self.cross_plot2.value_range.low = self.minz
        self.cross_plot2.value_range.high = self.maxz
        if self._image_index.metadata.has_key("selections"):
            x_ndx, y_ndx = self._image_index.metadata["selections"]
            if y_ndx and x_ndx:
                self.pd.set_data("line_value", 
                                 self._image_value.data[y_ndx,:])
                self.pd.set_data("line_value2", 
                                 self._image_value.data[:,x_ndx])
                xdata, ydata = self._image_index.get_data()
                xdata, ydata = xdata.get_data(), ydata.get_data()
                self.pd.set_data("scatter_index", array([xdata[x_ndx]]))
                self.pd.set_data("scatter_index2", array([ydata[y_ndx]]))
                self.pd.set_data("scatter_value",
                    array([self._image_value.data[y_ndx, x_ndx]]))
                self.pd.set_data("scatter_value2",
                    array([self._image_value.data[y_ndx, x_ndx]]))
                self.pd.set_data("scatter_color",
                    array([self._image_value.data[y_ndx, x_ndx]]))
                self.pd.set_data("scatter_color2",
                    array([self._image_value.data[y_ndx, x_ndx]]))
        else:
            self.pd.set_data("scatter_value", array([]))
            self.pd.set_data("scatter_value2", array([]))
            self.pd.set_data("line_value", array([]))
            self.pd.set_data("line_value2", array([]))
    def _colormap_changed(self):
        self._cmap = color_map_name_dict[self.colormap]
        if hasattr(self, "polyplot"):
            value_range = self.polyplot.color_mapper.range
            self.polyplot.color_mapper = self._cmap(value_range)
            value_range = self.cross_plot.color_mapper.range
            self.cross_plot.color_mapper = self._cmap(value_range)
            # FIXME: change when we decide how best to update plots using
            # the shared colormap in plot object
            self.cross_plot.plots["dot"][0].color_mapper = self._cmap(value_range)
            self.cross_plot2.plots["dot"][0].color_mapper = self._cmap(value_range)
            self.container.request_redraw()
    def _num_levels_changed(self):
        if self.num_levels > 3:
            self.polyplot.levels = self.num_levels
            self.lineplot.levels = self.num_levels
            
            
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
                menubar=MenuBar(Menu(Action(name="Load File", action="load_file"), # action= ... calls the function, given in the string
                                     Action(name="Save File", action="save_file"), 
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
            print 'update plot'
            self.plot_data.set_data('imagedata',self.model.intensity_map)
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
