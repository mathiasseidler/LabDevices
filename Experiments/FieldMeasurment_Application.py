
"""

"""

from enthought.traits.api import HasTraits, Str, Instance, Array, Button, Any, Enum, Int, Event,Trait, Callable, NO_COMPARE
from enthought.traits.ui.api import View, VGroup, HGroup, Item, Controller, Group, Tabbed
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
import thread, os
import datetime, time
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
from HandyClasses.IntensityFieldStageController import StageConfiguration, ThreadControl




class FieldData(HasTraits):
    """ Data and Index of the field
    """  
    __slots__ = 'intens_xy','intens_yz', 'intens_xz'
    intens_yz = Array(comparison_mode=NO_COMPARE)
    intens_xy = Array(comparison_mode=NO_COMPARE)
    intens_xz = Array(comparison_mode=NO_COMPARE)
    
class CaptureThread(Thread):
    def run(self):
        self.measure4()
    def measure4(self): 
        try:
            power_meter  = Thorlabs_PM100D("PM100D")
            stage       = TranslationalStage_3Axes('COM3','COM4')   
        except:
            print "Exception raised: Devices not available"
            return
        to_limit_speed = 2
        stage.AG_UC2_1.set_step_amplitude(1, self.sc.side_step_amplitude)
        stage.AG_UC2_1.set_step_amplitude(1, -self.sc.side_step_amplitude)
        stage.AG_UC2_1.set_step_amplitude(2, self.sc.bw_step_amplitude)
        stage.AG_UC2_1.set_step_amplitude(2, -self.sc.bw_step_amplitude)
        stage.AG_UC2_2.set_step_amplitude(1, self.sc.up_step_amplitude)
        stage.AG_UC2_2.set_step_amplitude(1, -self.sc.up_step_amplitude)        
        stage.AG_UC2_1.move_to_limit(1, -to_limit_speed)
        stage.AG_UC2_1.move_to_limit(2, -to_limit_speed)
        stage.AG_UC2_1.print_step_amplitudes()
        stage.AG_UC2_2.print_step_amplitudes()
        
        # acquire plane in yz-plane
        self.fd.intens_yz = zeros((self.sc.bw_steps, self.sc.side_steps))
        for i in range(0,self.sc.bw_steps):
            for j in range(0,self.sc.side_steps):
                if self.wants_abort:
                    return
                self.fd.intens_yz[i,j] = power_meter.getPower()
                stage.left(self.sc.side_steps_per_move)  
            stage.backwards(self.sc.bw_steps_per_move)
            stage.AG_UC2_1.move_to_limit(1, -to_limit_speed)
            self.fd.intens_yz = self.fd.intens_yz # this is to update the array for a traits callback
        #acquire vertical plane   
        stage.AG_UC2_1.move_to_limit(2,-to_limit_speed)
        max_index=unravel_index(self.fd.intens_yz.argmax(), self.fd.intens_yz.shape) # find index of the max intensity
        stage.left(max_index[1])
        print max_index
        stage.AG_UC2_2.move_to_limit(1,-to_limit_speed) 
        
        self.fd.intens_xz = zeros((self.sc.bw_steps, self.sc.up_steps))
        for i in range(0,self.sc.bw_steps):
            for j in range(0,self.sc.up_steps):
                if self.wants_abort:
                    return
                self.fd.intens_xz[i,j] = power_meter.getPower()
                stage.up(self.sc.up_steps_per_move)
            stage.backwards(self.sc.bw_steps_per_move)
            stage.AG_UC2_2.move_to_limit(1, -to_limit_speed)
            self.fd.intens_xz = self.fd.intens_xz
        
class CustomTool(BaseTool): 
    #right click
    def normal_right_down(self, event):
        '''
        on right click
        '''
        print event          
          
class GetBeamSectionThread(Thread):
    def run(self):
        self.get_beam_section()
        
    def get_beam_section(self):
        try:
            power_meter  = Thorlabs_PM100D("PM100D")
            stage       = TranslationalStage_3Axes('COM3','COM4')   
        except:
            print "Exception raised: Devices not available"
            return
        stage_config = self.sc
        field_data = self.fd
        to_limit_speed = 2
        stage.AG_UC2_1.set_step_amplitude(1, stage_config.side_step_amplitude)
        stage.AG_UC2_1.set_step_amplitude(1, -stage_config.side_step_amplitude)
        stage.AG_UC2_1.set_step_amplitude(2, stage_config.bw_step_amplitude)
        stage.AG_UC2_1.set_step_amplitude(2, -stage_config.bw_step_amplitude)
        stage.AG_UC2_2.set_step_amplitude(1, stage_config.up_step_amplitude)
        stage.AG_UC2_2.set_step_amplitude(1, -stage_config.up_step_amplitude)        
        stage.AG_UC2_1.move_to_limit(1, -to_limit_speed)
        stage.AG_UC2_2.move_to_limit(1, -to_limit_speed)
        stage.AG_UC2_1.print_step_amplitudes()
        stage.AG_UC2_2.print_step_amplitudes()
                
        field_data.intens_xy = zeros((stage_config.bw_steps, stage_config.side_steps))
        for i in range(0, stage_config.bw_steps):
            for j in range(0, stage_config.side_steps):
                if self.wants_abort:
                    return
                field_data.intens_xy[i,j] = power_meter.getPower()
                stage.left(stage_config.side_steps_per_move)  
            stage.up(stage_config.up_steps_per_move)
            stage.AG_UC2_1.move_to_limit(1, -to_limit_speed)
            field_data.intens_xy = field_data.intens_xy 

class GetHorizontalPlaneThread(Thread):
    def run(self):
        self.get_horizontal_plane()
        
    def get_horizontal_plane(self):
        try:
            power_meter  = Thorlabs_PM100D("PM100D")
            stage       = TranslationalStage_3Axes('COM3','COM4')   
        except:
            print "Exception raised: Devices not available"
            return
        stage_config = self.sc
        field_data = self.fd
        to_limit_speed = 2
        stage.AG_UC2_1.set_step_amplitude(1, stage_config.side_step_amplitude)
        stage.AG_UC2_1.set_step_amplitude(1, -stage_config.side_step_amplitude)
        stage.AG_UC2_1.set_step_amplitude(2, stage_config.bw_step_amplitude)
        stage.AG_UC2_1.set_step_amplitude(2, -stage_config.bw_step_amplitude)
        stage.AG_UC2_2.set_step_amplitude(1, stage_config.up_step_amplitude)
        stage.AG_UC2_2.set_step_amplitude(1, -stage_config.up_step_amplitude)        
        stage.AG_UC2_1.print_step_amplitudes()
        stage.AG_UC2_2.print_step_amplitudes()
        if not os.path.exists('../data/lensed_snom'):
            os.makedirs('../data/lensed_snom')

        for ind in range(0,50):
            stage.AG_UC2_1.move_to_limit(1, -to_limit_speed)
            stage.AG_UC2_1.move_to_limit(2, -to_limit_speed)
            field_data.intens_yz = zeros((stage_config.bw_steps, stage_config.side_steps))
            for i in range(0, stage_config.bw_steps):
                for j in range(0, stage_config.side_steps):
                    if self.wants_abort:
                        return
                    field_data.intens_yz[i,j] = power_meter.getPower()
                    stage.left(stage_config.side_steps_per_move)  
                stage.backwards(stage_config.bw_steps_per_move)
                stage.AG_UC2_1.move_to_limit(1, -to_limit_speed)
                field_data.intens_yz = field_data.intens_yz
            save('../data/lensed_snom/' + str(time.time()) + 'horizontal_plane', field_data.intens_yz) 
                        
class FieldDataController(HasTraits):
    
    model=Instance(FieldData,())
    plot_container=Instance(Component)
    plot_data=Instance(ArrayPlotData)
    _image_value = Instance(ImageData)
    renderer = Any()
    
    button_get_horizontal_plane = Button(label='Get horizontal plane')
    button_get_vertical_plane = Button(label= 'Get vertical plane')
    button_get_section = Button(label = 'Get beam section')
    
    update = Event
    
    sc = Instance(StageConfiguration,())
    thread_control = Event
    capture_thread = Instance(CaptureThread)
    get_beam_section_thread = Instance(GetBeamSectionThread)
    horizontal_plane_thread = Instance(GetHorizontalPlaneThread)
    label_button_measurment = Str('Start acquisition')
    
    _save_file = File('default.npy', filter=['Numpy files (*.npy)| *.npy'])
    _load_file = File('.npy',  filter=['Numpy files (*.npy) | *.npy', 'All files (*.*) | *.*'])
    # Define the view associated with this controller:
    view = View(HGroup(VGroup(Item('thread_control' , label='', editor = ButtonEditor(label_value = 'label_button_measurment')),
    'button_get_horizontal_plane'), VGroup('button_get_vertical_plane', 'button_get_section')),
                Item('sc',style='custom',show_label=False),
                Item('plot_container',editor=ComponentEditor(),show_label=False),
                menubar=MenuBar(Menu("_",Action(name="Load data", action="load_file"), # action= ... calls the function, given in the string
                                     Action(name="Save data", action="save_file"), 
                                    '_',
                                    CloseAction,
                                    name="File")),
                resizable=True,
                width=700)
    
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

        self.model.intens_xy = array([[]])
        self.model.intens_xz = array([[]])
        self.model.intens_yz = array([[]])
        # Create a plot data obect and give it this data
        self.create_plot_component()
        
    def create_plot_component(self):
        self.plot_data = ArrayPlotData()
        self.plot_data.set_data("imagedata", self.model.intens_yz)
        self.plot_data.set_data('vert_image',self.model.intens_xz)
        self.plot_data.set_data('beam_section', self.model.intens_xy)
        # Create a contour polygon plot of the data
        plot = Plot(self.plot_data)
        plot.title = 'Horizontal plane'
        plot.padding=5
        plot.padding_top = 22
        plot.padding_left=25
        plot.padding_bottom=20
        my_plot = plot.img_plot("imagedata", name='my_plot', # xbounds=x,#ybounds=y,
                             colormap=jet, hide_grids=True)[0]
        
        colormap = my_plot.color_mapper
        colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                        color_mapper=colormap,
                        plot=my_plot,
                        orientation='v',
                        resizable='v',
                        width=25,
                        padding=0)      
        colorbar.padding_top = plot.padding_top
        colorbar.padding_bottom = plot.padding_bottom
        colorbar.padding_left = 35
        colorbar.padding_right = 30                                         
        colorbar._axis.tick_label_formatter = lambda x: ('%.0e'%x)                     
                             
        rplot = Plot(self.plot_data)
        rplot.title = 'Vertical plane'
        rplot.padding=plot.padding
        rplot.padding_top = plot.padding_top
        rplot.padding_left = plot.padding_left
        rplot.padding_bottom = plot.padding_bottom   
        my_plot = rplot.img_plot('vert_image',name='vert_plot',colormap=jet)[0]
        colormap = my_plot.color_mapper
        colorbar_rplot = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                        color_mapper=colormap,
                        plot=my_plot,
                        orientation='v',
                        resizable='v',
                        width=25,
                        padding=0)      
        colorbar_rplot.padding_top = plot.padding_top
        colorbar_rplot.padding_bottom = plot.padding_bottom
        colorbar_rplot.padding_right = 20
        colorbar_rplot.padding_left = 35    
        colorbar_rplot._axis.tick_label_formatter = lambda x: ('%.0e'%x) 
           
        sec_plot = Plot(self.plot_data)
        sec_plot.title = 'Beam section'
        sec_plot.padding=plot.padding
        sec_plot.padding_top = plot.padding_top
        sec_plot.padding_left = plot.padding_left
        sec_plot.padding_bottom = plot.padding_bottom   
        my_plot = sec_plot.img_plot('beam_section',name='beam_section_plot',colormap=jet)[0]
        colormap = my_plot.color_mapper
        colorbar_sec_plot = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                        color_mapper=colormap,
                        plot=my_plot,
                        orientation='v',
                        resizable='v',
                        width=25,
                        padding=0)      
        colorbar_sec_plot.padding_top = plot.padding_top
        colorbar_sec_plot.padding_bottom = plot.padding_bottom
        colorbar_sec_plot.padding_right = 20
        colorbar_sec_plot.padding_left = 35    
        colorbar_sec_plot._axis.tick_label_formatter = lambda x: ('%.0e'%x)    
        container = HPlotContainer(use_backbuffer = True)
        container.add(plot)
        container.add(colorbar)
        container.add(rplot)
        container.add(colorbar_rplot)
        container.add(sec_plot)
        container.add(colorbar_sec_plot)
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
            self.capture_thread.sc = self.sc
            self.capture_thread.start()
            self.label_button_measurment = 'Stop acquisition'
            
    def _step_amplitude_changed(self):
        if self.capture_thread:
            self.capture_thread.stepamplitude = self.step_amplitude
    
    def _update_fired(self):
        self.create_plot_component()
        
    def _button_get_section_fired(self):
        if self.get_beam_section_thread and self.get_beam_section_thread.isAlive():
            self.get_beam_section_thread.wants_abort = True
            #self.label_button_measurment = 'Start acquisition'
        else:
            self.get_beam_section_thread = GetBeamSectionThread()
            self.get_beam_section_thread.wants_abort = False
            self.get_beam_section_thread.fd = self.model
            self.get_beam_section_thread.plotdata= self.plot_data
            self.get_beam_section_thread.sc = self.sc
            self.get_beam_section_thread.start()
            #self.label_button_measurment = 'Stop acquisition'    
    
    def _button_get_vertical_plane_fired(self):
        print 'vertical plane'
        
    def _button_get_horizontal_plane_fired(self):
        if self.horizontal_plane_thread and self.horizontal_plane_thread.isAlive():
            self.horizontal_plane_thread.wants_abort = True
            #self.label_button_measurment = 'Start acquisition'
        else:
            self.horizontal_plane_thread = GetHorizontalPlaneThread()
            self.horizontal_plane_thread.wants_abort = False
            self.horizontal_plane_thread.fd = self.model
            self.horizontal_plane_thread.plotdata= self.plot_data
            self.horizontal_plane_thread.sc = self.sc
            self.horizontal_plane_thread.start()
        
    @on_trait_change('model.intens_yz')        
    def update_plot(self,name,old,new):
        if self.plot_data and new.ndim > 1:
            self.create_plot_component()
            #self.plot_data.set_data('imagedata', new)
            
    @on_trait_change('model.intens_xz')        
    def update_rplot(self,name,old,new):
        if self.plot_data and new.ndim > 1:
            self.create_plot_component()
            
    @on_trait_change('model.intens_xy')        
    def update_sec_plot(self,name,old,new):
        if self.plot_data and new.ndim > 1:
            self.create_plot_component()
    def save_file(self):
        """
        Callback for the 'Save Image' menu option.
        """
        ui = self.edit_traits(view='save_file_view')
        if ui.result == True:
            save(self._save_file, self.model.intens_xz)
            save(self._save_file + '_vertical',self.model.intens_yz)
            
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
                self.model.intens_xy = load(self._load_file)
            except:
                print 'Loading the file failed'
            
        
    
ui = FieldDataController()
ui.configure_traits(view='view')
