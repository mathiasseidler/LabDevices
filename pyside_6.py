'''
Created on Feb 20, 2012

@author: Mathias
'''
import sys
from numpy import arange, sin, array
from PySide.QtCore import *
from PySide.QtGui import *

app = QApplication(sys.argv)

from enthought.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"
#from enthought.enable.api import Window
#from enthought.chaco.api import ArrayPlotData, Plot

from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import View, Item
from enthought.chaco.api import Plot, ArrayPlotData
from enthought.enable.component_editor import ComponentEditor
from numpy import linspace, sin

class ScatterPlot(HasTraits):
    plot = Instance(Plot)
    traits_view = View(
        Item('plot',editor=ComponentEditor(), show_label=False),
        width=500, height=500, resizable=True, title="Chaco Plot")

    def __init__(self):
        super(ScatterPlot, self).__init__()
        x = linspace(-14, 14, 100)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x = x, y = y)
        plot = Plot(plotdata)
        plot.plot(("x", "y"), type="scatter", color="blue")
        plot.title = "sin(x) * x^3"
        self.plot = plot

if __name__ == "__main__":
    ScatterPlot().configure_traits()