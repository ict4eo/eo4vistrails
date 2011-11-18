############################################################################
###
### Copyright (C) 2011 CSIR Meraka Institute. All rights reserved.
###
### eo4vistrails extends VisTrails, providing GIS/Earth Observation
### ingestion, pre-processing, transformation, analytic and visualisation
### capabilities . Included is the abilty to run code transparently in
### OpenNebula cloud environments. There are various software
### dependencies, but all are FOSS.
###
### This file may be used under the terms of the GNU General Public
### License version 2.0 as published by the Free Software Foundation
### and appearing in the file LICENSE.GPL included in the packaging of
### this file.  Please review the following to ensure GNU General Public
### Licensing requirements will be met:
### http://www.opensource.org/licenses/gpl-license.php
###
### If you are unsure which license is appropriate for your use (for
### instance, you are interested in developing a commercial derivative
### of VisTrails), please contact us at vistrails@sci.utah.edu.
###
### This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
### WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
###
#############################################################################
"""This module provides extended plotting capabilities for EO4VisTrails.

This module  is based on the vistrails.packages.pylab module, but with
extended plotting types and configuration options.

"""

# library
import time
import urllib
# third party
# vistrails
from core.bundles import py_import
import core.modules
import core.modules.module_registry
from core import debug
from core.modules import basic_modules
from core.modules.basic_modules import File, String, Boolean
from core.modules.vistrails_module import Module, NotCacheable, InvalidOutput
from packages.pylab.plot import MplPlot, MplPlotConfigurationWidget
# eo4vistrails
from packages.eo4vistrails.utils.DropDownListWidget import ComboBoxWidget
# local


try:
    mpl_dict = {'linux-ubuntu': 'python-matplotlib',
                'linux-fedora': 'python-matplotlib'}
    matplotlib = py_import('matplotlib', mpl_dict)
    matplotlib.use('Qt4Agg')
    pylab = py_import('pylab', mpl_dict)
except Exception, e:
    debug.critical("Exception: %s" % e)


class StandardHistogram(NotCacheable, Module):
    _input_ports = [('columnData', '(edu.utah.sci.vistrails.basic:List)'),
                    ('title', '(edu.utah.sci.vistrails.basic:String)'),
                    ('xlabel', '(edu.utah.sci.vistrails.basic:String)'),
                    ('ylabel', '(edu.utah.sci.vistrails.basic:String)'),
                    ('bins', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('facecolor', '(edu.utah.sci.vistrails.basic:Color)')]
    _output_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

    def compute(self):
        data = [float(x) for x in self.getInputFromPort('columnData')]
        fig = pylab.figure()
        pylab.setp(fig, facecolor='w')
        if self.hasInputFromPort('title'):
            pylab.title(self.getInputFromPort('title'))
        if self.hasInputFromPort('xlabel'):
            pylab.xlabel(self.getInputFromPort('xlabel'))
        if self.hasInputFromPort('ylabel'):
            pylab.ylabel(self.getInputFromPort('ylabel'))
        if self.hasInputFromPort('bins'):
            bins = self.getInputFromPort('bins')
        else:
            bins = 10
        if self.hasInputFromPort('facecolor'):
            color = self.getInputFromPort('facecolor').tuple
        else:
            color = 'b'
        pylab.hist(data, bins, facecolor=color)
        pylab.get_current_fig_manager().toolbar.hide()
        self.setResult('source', "")


class StandardPlot(NotCacheable, Module):
    _input_ports = [('xData', '(edu.utah.sci.vistrails.basic:List)'),
                    ('yData', '(edu.utah.sci.vistrails.basic:List)'),
                    ('plot', '(za.co.csir.eo4vistrails:Plot Type:plots)'),
                    ('marker', '(za.co.csir.eo4vistrails:Plot Marker:plots)'),
                    ('title', '(edu.utah.sci.vistrails.basic:String)'),
                    ('xlabel', '(edu.utah.sci.vistrails.basic:String)'),
                    ('ylabel', '(edu.utah.sci.vistrails.basic:String)'),
                    ('facecolor', '(edu.utah.sci.vistrails.basic:Color)')]
    _output_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

    def compute(self):
        plot_type = self.getInputFromPort('plot') or 'scatter'
        marker_type = self.getInputFromPort('marker') or 's'
        x_data = [float(x) for x in self.getInputFromPort('xData')]
        y_data = [float(y) for y in self.getInputFromPort('yData')]
        fig = pylab.figure()
        # pylab.setp(fig, facecolor='w')
        if self.hasInputFromPort('title'):
            pylab.title(self.getInputFromPort('title'))
        if self.hasInputFromPort('xlabel'):
            pylab.xlabel(self.getInputFromPort('xlabel'))
        if self.hasInputFromPort('ylabel'):
            pylab.ylabel(self.getInputFromPort('ylabel'))
        if self.hasInputFromPort('facecolor'):
            color = self.getInputFromPort('facecolor').tuple
        else:
            color = 'r'

        if plot_type == 'scatter':
            pylab.scatter(x_data, y_data, marker=marker_type, facecolor=color)
        elif plot_type == 'dates':
            # TODO - get date-formatted from x-data
            pylab(x_data, y_data, marker=marker_type, facecolor=color)
        elif plot_type == 'line':
            pylab(x_data, y_data, marker=marker_type, facecolor=color)
        else:
            pass

        pylab.get_current_fig_manager().toolbar.hide()
        self.setResult('source', "")


class StandardWindrose(NotCacheable, Module):
    _input_ports = [('direction', '(edu.utah.sci.vistrails.basic:List)'),
                    ('variable', '(edu.utah.sci.vistrails.basic:List)'),
                    ('title', '(edu.utah.sci.vistrails.basic:String)'),
                    ('xlabel', '(edu.utah.sci.vistrails.basic:String)'),
                    ('ylabel', '(edu.utah.sci.vistrails.basic:String)'),
                    ('facecolor', '(edu.utah.sci.vistrails.basic:Color)')]
    _output_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

    def compute(self):
        pass


class MatplotlibMarkerComboBoxWidget(ComboBoxWidget):
    """Marker constants used for drawing markers on a matplotlib plot."""
    _KEY_VALUES = {'#': '#', '+': '+', ',': ',', 'o': 'o', '.': '.',
                   's': 's', 'v': 'v', 'x': 'x', '>': '>', '<': '<',
                   '^': '^'}

MatplotlibMarkerComboBox = basic_modules.new_constant('Plot Marker',
                                        staticmethod(str),
                                        's',
                                        staticmethod(lambda x: type(x) == str),
                                        MatplotlibMarkerComboBoxWidget)


class MatplotlibPlotTypeComboBoxWidget(ComboBoxWidget):
    """matplotlib plot types."""
    _KEY_VALUES = {'scatter': 'Scatter', 'line': 'Line'}

MatplotlibPlotTypeComboBox = basic_modules.new_constant('Plot Type',
                                        staticmethod(str),
                                        'scatter',
                                        staticmethod(lambda x: type(x) == str),
                                        MatplotlibPlotTypeComboBoxWidget)
