# Authors: Prabhu Ramachandran <prabhu [at] aero.iitb.ac.in>
# Copyright (c) 2007, Enthought, Inc.
# License: BSD Style.

# Standard imports.
from numpy import sqrt, sin, mgrid, ogrid

# Enthought imports.
from traits.api import HasTraits, Instance, Property, Enum
from traitsui.api import View, Item, HSplit, VSplit, InstanceEditor
from tvtk.pyface.scene_editor import SceneEditor
from mayavi.core.ui.engine_view import EngineView
from mayavi.tools.mlab_scene_model import MlabSceneModel
from mayavi import mlab

class Mayavi(HasTraits):

    # The scene model.
    scene = Instance(MlabSceneModel, ())
    # The mayavi engine view.
    engine_view = Instance(EngineView)
    ######################
    view = View(HSplit(Item(name='engine_view',
                                   style='custom',
                                   resizable=True,
                                   show_label=False
                                   ),
                               Item(name='scene',
                                    editor=SceneEditor(),
                                    show_label=False,
                                    resizable=True,
                                    height=500,
                                    width=500)
                        ),
                resizable=True,
                scrollable=True
                )

    def __init__(self, **traits):
        HasTraits.__init__(self, **traits)
        self.engine_view = EngineView(engine=self.scene.engine)

        # Hook up the current_selection to change when the one in the engine
        # changes.  This is probably unnecessary in Traits3 since you can show
        # the UI of a sub-object in T3.
        #self.scene.engine.on_trait_change(self._selection_change,
        #                                  'current_selection')

        self.generate_data_mayavi()

    def generate_data_mayavi(self):
        """Shows how you can generate data using mayavi instead of mlab."""
        #from mayavi.sources.api import ParametricSurface
        #from mayavi.modules.api import Outline, Surface
        x, y, z = ogrid[-10:10:20j, -10:10:20j, -10:10:20j]
        s = sin(x*y*z)/(x*y*z)
        e = self.scene.engine
        #s = ParametricSurface()
        #e.add_source(s)
        #e.add_module(Outline())
        #e.add_module(Surface())
        #mlab.pipeline.volume(mlab.pipeline.scalar_field(s), vmin=0.2, vmax=0.8)
        
        src = mlab.pipeline.scalar_field(s)
        mlab.pipeline.iso_surface(src, contours=[s.min()+0.1*s.ptp(), ], opacity=0.1)
        mlab.pipeline.iso_surface(src, contours=[s.max()-0.1*s.ptp(), ],)
        mlab.pipeline.image_plane_widget(src,
                            plane_orientation='z_axes',
                            slice_index=10,
                        )

    def _selection_change(self, old, new):
        self.trait_property_changed('current_selection', old, new)

    def _get_current_selection(self):
        return self.scene.engine.current_selection
    
if __name__ == '__main__':
    m = Mayavi()
    m.configure_traits()