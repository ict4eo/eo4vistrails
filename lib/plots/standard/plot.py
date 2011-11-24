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

This module is based on the vistrails.packages.pylab module, but with
extended plotting types and configuration options.

Development Notes
==================

#For multiple graphs ...

import matplotlib.pyplot as plt

plt.figure(1)
plt.plot(range(10),range(10))

plt.figure(2)
plt.plot(range(2),range(2))

"""

# library
import time
import urllib
from datetime import datetime
import random
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
from packages.eo4vistrails.lib.plots.windrose.windrose import WindroseAxes
# local


try:
    mpl_dict = {'linux-ubuntu': 'python-matplotlib',
                'linux-fedora': 'python-matplotlib'}
    matplotlib = py_import('matplotlib', mpl_dict)
    matplotlib.use('Qt4Agg')
    pylab = py_import('pylab', mpl_dict)
except Exception, e:
    debug.critical("Exception: %s" % e)


class ParentPlot(NotCacheable, Module):
    """Provide common routines and data for all plot modules."""

    def to_float(self, s):
        try:
            return float(s)
        except:
            return ''

    def to_str(self, s):
        if s:
            return str(s)
        else:
            return ''

    def to_date(self, x, DATE_FORMAT):
        try:
            return matplotlib.dates.date2num(datetime.strptime(x, DATE_FORMAT))
        except:
            return None

    def compute(self):
        pass


class StandardHistogram(ParentPlot):
    _input_ports = [('columnData', '(edu.utah.sci.vistrails.basic:List)'),
                    ('title', '(edu.utah.sci.vistrails.basic:String)'),
                    ('xAxis_label', '(edu.utah.sci.vistrails.basic:String)'),
                    ('yAxis_label', '(edu.utah.sci.vistrails.basic:String)'),
                    ('bins', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('facecolor', '(edu.utah.sci.vistrails.basic:Color)')]
    _output_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

    def compute(self):
        data = [self.to_float(x) for x in self.getInputFromPort('columnData')]
        bins = self.forceGetInputFromPort('bins', 10)
        if self.hasInputFromPort('facecolor'):
            self.facecolor = self.getInputFromPort('facecolor').tuple
        else:
            self.facecolor = 'w'

        fig = pylab.figure()
        pylab.setp(fig, facecolor=self.facecolor)
        if self.hasInputFromPort('title'):
            pylab.title(self.getInputFromPort('title'))
        if self.hasInputFromPort('xAxis_label'):
            pylab.xlabel(self.getInputFromPort('xAxis_label'))
        if self.hasInputFromPort('yAxis_label'):
            pylab.ylabel(self.getInputFromPort('yAxis_label'))

        pylab.hist(data, bins, facecolor=color)
        pylab.get_current_fig_manager().toolbar.hide()
        self.setResult('source', "")


class StandardPlot(ParentPlot):
    """Allow a single series to be plotted.

    Input ports:
        xyData:
            a list containing two lists - one of X data values,
            and one of Y data values.  For:
            * windrose plots, X data values are wind direction;
            * date(x) plots, X data values are dates.
        plot:
            the type of plot (line, scatter, date(x), windrose)
        line_style:
            the type of line style (defaults to solid)
        marker:
            the type of marker (defaults to square)
        title:
            an optional title that will appear above the plot
        xAxis_label:
            an optional label for the X-axis (ignored for windrose)
        yAxis_label:
            an optional label for the Y-axis (ignored for windrose)
        facecolor:
            the color for the marker face (plot color for windrose)

    Output ports:
        source:
            the matplotlib source code for the plot

    """
    _input_ports = [('xyData', '(edu.utah.sci.vistrails.basic:List)'),
                    ('plot', '(za.co.csir.eo4vistrails:Plot Type:plots)'),
                    ('marker', '(za.co.csir.eo4vistrails:Plot Marker:plots)'),
                    ('line_style', '(za.co.csir.eo4vistrails:Plot Line Style:plots)'),
                    ('title', '(edu.utah.sci.vistrails.basic:String)'),
                    ('xAxis_label', '(edu.utah.sci.vistrails.basic:String)'),
                    ('yAxis_label', '(edu.utah.sci.vistrails.basic:String)'),
                    ('facecolor', '(edu.utah.sci.vistrails.basic:Color)')]
    _output_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

    def new_axes(self):
        fig = pylab.figure(figsize=(8, 8), dpi=80, facecolor=self.facecolor,
                         edgecolor='w')
        rect = [0.1, 0.1, 0.8, 0.8]
        ax = WindroseAxes(fig, rect, axisbg=self.facecolor)
        fig.add_axes(ax)
        return ax

    def set_legend(self, ax):
        l = ax.legend(axespad=-0.10)
        pylab.setp(l.get_texts(), fontsize=8)

    def create_rose(self, value, direction):
        if direction and value:
            ax = self.new_axes()
            ax.bar(direction, value, normed=True, opening=0.8, edgecolor='w')
            self.set_legend(ax)
            if self.hasInputFromPort('title'):
                ax.set_title(self.getInputFromPort('title'))
            return ax
        else:
            print "wind direction and/or value are null..."
            return None

    def compute(self):
        plot_type = self.forceGetInputFromPort('plot', 'scatter')
        marker_type = self.forceGetInputFromPort('marker', 's')
        line_style = self.forceGetInputFromPort('line_style', '-')
        if self.hasInputFromPort('facecolor'):
            self.facecolor = self.getInputFromPort('facecolor').tuple
        else:
            self.facecolor = 'r'

        xyData = self.forceGetInputFromPort('xyData', [])
        if xyData and len(xyData) == 2:
            y_data = [float(y) for y in xyData[1]]
            fig = pylab.figure()
            if self.hasInputFromPort('title'):
                pylab.title(self.getInputFromPort('title'))
            if self.hasInputFromPort('xAxis_label'):
                pylab.xlabel(self.getInputFromPort('xAxis_label'))
            if self.hasInputFromPort('yAxis_label'):
                pylab.ylabel(self.getInputFromPort('yAxis_label'))

            if plot_type == 'date':
                #matplotlib.dates.date2num(d) #d is either a datetime instance or a sequence of datetimes.
                DATE_FORMAT = '%Y-%m-%d'  # pass this in as option?
                x_data = [self.to_date(self, x, DATE_FORMAT) for x in xyData[0]]
                pylab.plot_date(x_data, y_data, xdate=True, marker=marker_type,
                                markerfacecolor=self.facecolor)
                fig.autofmt_xdate()  # pretty-format date axis
            else:
                x_data = [self.to_float(x) for x in xyData[0]]
                if plot_type == 'scatter':
                    pylab.scatter(x_data, y_data, marker=marker_type, facecolor=self.facecolor)
                elif plot_type == 'line':
                    pylab.plot(x_data, y_data, marker=marker_type,
                               linestyle=line_style, markerfacecolor=self.facecolor)
                elif plot_type == 'windrose':
                    fig = self.create_rose(y_data, x_data)
                else:
                    pass

        pylab.get_current_fig_manager().toolbar.hide()
        self.setResult('source', "")


class MultiPlot(ParentPlot):
    """Allow multiple series to be plotted on the same plot.

    Input ports:
        datasets:
            a list of lists - the first list is the X values, and the second
            and subsequent sets are the Y values.  X-values can be numeric or
            dates, but Y-values must be numeric.
        plot:
            the type of plot
        title:
            a title that will appear above the plot
        xAxis_label:
            the label for the X-axis
        yAxis_label:
            the label for the Y-axis

    Output ports:
        source:
            the matplotlib source code for the plot

    """
    _input_ports = [('datasets', '(edu.utah.sci.vistrails.basic:List)'),
                    ('plot', '(za.co.csir.eo4vistrails:Plot Type:plots)'),
                    ('title', '(edu.utah.sci.vistrails.basic:String)'),
                    ('xAxis_label', '(edu.utah.sci.vistrails.basic:String)'),
                    ('yAxis_label', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

    def compute(self):
        MARKER = ('o', 'd', '*', '+', 's', 'v', 'x',  '>', '<', '^', 'h', )
        line_style = '-'
        plot_type = self.forceGetInputFromPort('plot', 'scatter')
        if self.hasInputFromPort('datasets'):
            data_sets = self.getInputFromPort('datasets')
        else:
            data_sets = []
        print "plot:271", data_sets

        fig = pylab.figure()
        if self.hasInputFromPort('title'):
            pylab.title(self.getInputFromPort('title'))
        if self.hasInputFromPort('xAxis_label'):
            pylab.xlabel(self.getInputFromPort('xAxis_label'))
        if self.hasInputFromPort('yAxis_label'):
            pylab.ylabel(self.getInputFromPort('yAxis_label'))

        ax = pylab.subplot(111)
        max_markers = len(MARKER)

        if data_sets:
            x_series = data_sets[0]
            print "plot:283", x_series
            for key, dataset in enumerate(data_sets):
                if key:  # skip first series (used for X-axis data)
                    marker_number = key - (max_markers * int(key / max_markers)) - 1
                    y_data = [self.to_float(y) for y in dataset]
                    hexcode = "#%x" % random.randint(0, 16777215)
                    self.facecolor = hexcode.ljust(7).replace(' ', '0')
                    print "plot:291", key, marker_number, y_data
                    if plot_type == 'date':
                        DATE_FORMAT = '%Y-%m-%d'  # pass this in as option?
                        x_data = [self.to_date(x, DATE_FORMAT) for x in x_series]
                        ax.plot_date(x_data, y_data, xdate=True,
                                        marker=MARKER[marker_number],
                                        markerfacecolor=self.facecolor)
                        fig.autofmt_xdate()  # pretty-format date axis
                    elif plot_type == 'scatter':
                        x_data = [self.to_float(x) for x in x_series]
                        ax.scatter(x_data, y_data, marker=MARKER[marker_number],
                                   facecolor=self.facecolor)
                    elif plot_type == 'line':
                        x_data = [self.to_float(x) for x in x_series]
                        ax.plot(x_data, y_data, marker=MARKER[marker_number],
                                linestyle=line_style,
                                markerfacecolor=self.facecolor)
                    else:
                        pass

        pylab.get_current_fig_manager().toolbar.hide()
        self.setResult('source', "")


class MatplotlibMarkerComboBoxWidget(ComboBoxWidget):
    """Marker constants used for drawing markers on a matplotlib plot."""
    _KEY_VALUES = {'plus': '+', 'circle': 'o', 'diamond': 'd', 'star': '*',
                   'square': 's', 'cross': 'x', 'hexagon': 'h',
                   'triangle_down': 'v', 'triangle_right': '>',
                   'triangle_left': '<', 'triangle_up': '^', }

MatplotlibMarkerComboBox = basic_modules.new_constant('Plot Marker',
                                        staticmethod(str),
                                        's',
                                        staticmethod(lambda x: type(x) == str),
                                        MatplotlibMarkerComboBoxWidget)


class MatplotlibLineStyleComboBoxWidget(ComboBoxWidget):
    """Marker constants used for drawing markers on a matplotlib plot."""
    _KEY_VALUES = {'solid': '-', 'dashed': '--', 'dash-dot': '-.', 'dotted': ':'}

MatplotlibLineStyleComboBox = basic_modules.new_constant('Plot Line Style',
                                        staticmethod(str),
                                        '-',
                                        staticmethod(lambda x: type(x) == str),
                                        MatplotlibLineStyleComboBoxWidget)


class MatplotlibPlotTypeComboBoxWidget(ComboBoxWidget):
    """matplotlib plot types."""
    _KEY_VALUES = {'scatter': 'scatter', 'line': 'line', 'date(x)': 'date',
                   'windrose': 'windrose'}

MatplotlibPlotTypeComboBox = basic_modules.new_constant('Plot Type',
                                        staticmethod(str),
                                        'scatter',
                                        staticmethod(lambda x: type(x) == str),
                                        MatplotlibPlotTypeComboBoxWidget)




def to_str(self, s):
    try:
        return str(s)
    except:
        return ''