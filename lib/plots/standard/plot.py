# -*- coding: utf-8 -*-
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
"""

# library
import time
import urllib
from datetime import datetime
import random
from numpy import array, ma
# third party
# vistrails
from core.bundles import py_import
import core.modules
import core.modules.module_registry
from core import debug
from core.modules import basic_modules
from core.modules.basic_modules import File, String, Boolean
from core.modules.vistrails_module import Module, ModuleError, NotCacheable, \
                                          InvalidOutput
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
    """Provides common routines and data for all plot modules."""

    MISSING = 1e-8  # used by numpy as a "placeholder" for missing values

    def random_color(self):
        """Returns a 6-digit random hex color."""
        hexcode = "#%x" % random.randint(0, 16777215)
        return hexcode.ljust(7).replace(' ', '0')

    def to_float(self, string):
        """Returns a float from a string, or 'almost zero' if invalid."""
        try:
            return float(string)
        except:
            return self.MISSING

    def to_str(self, string):
        """Returns a string, or an empty string if None."""
        if string:
            return str(string)
        else:
            return ''

    def to_date(self, string, date_format):
        """Returns a date from a string, in the specified date format,
        or 'almost zero' if invalid.

        Notes:
         *  Uses matplotlib.dates.date2num(d), where:
                d is either a datetime instance or a sequence of datetimes.
        """
        try:
            return matplotlib.dates.date2num(datetime.strptime(
                                                        string, date_format))
        except:
            return self.MISSING

    def list_to_floats(self, items, mask=True):
        """Convert a list into a list of floating point values.

        mask:
            replace None or empty strings with a MISSING value
        """
        if not items:
            return None
        data = [self.to_float(x) for x in items]
        if mask:
            return ma.masked_values(data, self.MISSING)  # ignores missing data
        else:
            return data

    def list_to_dates(self, items, date_format='%Y-%m-%d'):
        """Convert a list into a list of masked date values, with each date
        in the specified date format.

        Notes:
         *  matplotlib seems to require date data in the form '%Y-%m-%d'
        """
        if not items:
            return None
        x_data = [self.to_date(x, date_format) for x in items]
        return ma.masked_values(x_data, 1e-8)  # ignore missing data

    def all_the_same(self, vals):
        ''' Test if vals is an iterable whose elements are all equal.

        Notes:
         *  http://mail.python.org/pipermail/tutor/2004-November/033394.html
        '''

        i = iter(vals)  # Raises TypeError if vals is not a sequence
        try:
            first = i.next()
        except StopIteration:
            # vals is an empty sequence
            return True
        for item in i:
            if first != item:
                return False
        return True

    def compute(self):
        pass


class Histogram(ParentPlot):
    """Allows single or multiple series to be plotted as a histogram.

    Input ports:
        columnData:
            a list containing one or more lists - each list contains a string
            of common-separated numeric data values
        plot:
            the type of histogram (bar, step, barstacked, stepfilled)
        title:
            an optional title that will appear above the plot
        xAxis_label:
            an optional label for the X-axis
        yAxis_label:
            an optional label for the Y-axis
        facecolor:
            the color for the face of the single-series bars
        bins:
            the number of bins into which to group the data
        cumulative:
            switch to indicate if the data should be accumulated

    Output ports:
        source:
            the matplotlib source code for the plot

    Notes:
     *  The matplotlib `cbook` module is extremely useful for data conversion

    """

    _input_ports = [('columnData', '(edu.utah.sci.vistrails.basic:List)'),
                    ('plot', '(za.co.csir.eo4vistrails:Histogram Type:plots)'),
                    ('title', '(edu.utah.sci.vistrails.basic:String)'),
                    ('xAxis_label', '(edu.utah.sci.vistrails.basic:String)'),
                    ('yAxis_label', '(edu.utah.sci.vistrails.basic:String)'),
                    ('facecolor', '(edu.utah.sci.vistrails.basic:Color)'),
                    ('bins', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('cumulative', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ]
    _output_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

    def compute(self):
        data_in = self.getInputFromPort('columnData')
        hist_type = self.forceGetInputFromPort('plot', 'bar')
        cumulative = self.forceGetInputFromPort('cumulative', False)
        bins = self.forceGetInputFromPort('bins', 10)

        fig = pylab.figure()
        pylab.setp(fig, facecolor='w')  # background color
        if self.hasInputFromPort('title'):
            pylab.title(self.getInputFromPort('title'))
        if self.hasInputFromPort('xAxis_label'):
            pylab.xlabel(self.getInputFromPort('xAxis_label'))
        if self.hasInputFromPort('yAxis_label'):
            pylab.ylabel(self.getInputFromPort('yAxis_label'))
        if self.hasInputFromPort('facecolor'):
            self.facecolor = self.getInputFromPort('facecolor').tuple
        else:
            self.facecolor = 'r'  # bar color for single series

        dataset = []
        if all(isinstance(item, list) for item in data_in):
            if len(data_in) > 1:
                # this is a 'list of lists' (multi-series)
                # NOTE: ranges are being tracked manually as pylab.hist appears
                #   to only track max/min for the first series/array.
                combined = []
                ranges = []
                lengths = []
                for item in data_in:
                    floats = self.list_to_floats(item)
                    compress = array(floats.compressed())  # remove masked vals
                    lengths.append(len(compress))  # track series' length
                    combined.append(compress)
                    ranges.append(compress.max())
                    ranges.append(compress.min())
                range_max = array(ranges).max()
                range_min = array(ranges).min()
                #print "plot:214-combined", combined, range_min, range_max
                if self.all_the_same(lengths):
                    # pylab.hist FAILS if all series have the same length:
                    # http://old.nabble.com/Inconsistent-behavior-in-plt.hist-tt27857685.html
                    # http://old.nabble.com/Problem-with-hist-td25925830.html
                    raise ModuleError(self,
                                      "All series cannot be the same length...")
                else:
                    pylab.hist(combined, bins, histtype=hist_type,
                               range=(range_min, range_max),
                               cumulative=cumulative)

            elif len(data_in) == 1:
                # a single nested list (single-series)
                dataset.append(self.list_to_floats(data_in[0]))
                pylab.hist(dataset[0], bins, histtype=hist_type,
                           cumulative=cumulative, facecolor=self.facecolor)

            else:
                pass  # length '0' list containing no data...
        else:
            # a set of normal values (not contained in nested list)
            dataset = self.list_to_floats(data_in)
            #print "plot:258", dataset, "\n bins", bins, "\n cumu", cumulative,\
            #    "\n face", self.facecolor
            pylab.hist(dataset, bins, histtype=hist_type,
                       cumulative=cumulative, facecolor=self.facecolor)

        pylab.get_current_fig_manager().toolbar.hide()
        self.setResult('source', "")


class SinglePlot(ParentPlot):
    """Allows a single series to be plotted.

    Input ports:
        xyData:
            a list containing two lists - one with the X-axis values,
            and one with the Y-axis numeric data values. For:
            * windrose plots, X data points are wind directions (numeric values)
            * date(x) plots, X data points are date values
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
            the color for the face of the markers (plot color for windrose)

    Output ports:
        source:
            the matplotlib source code for the plot

    Notes:
     *  The matplotlib cbook module is extremely useful for data conversion

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

    def create_rose(self, value, direction):
        if len(direction) > 0 and len(value) > 0:
            ax = self.new_axes()
            ax.bar(direction, value, normed=True, opening=0.8, edgecolor='w')
            l = ax.legend(borderaxespad=-0.10)
            pylab.setp(l.get_texts(), fontsize=8)
            if self.hasInputFromPort('title'):
                ax.set_title(self.getInputFromPort('title'))
            return ax
        else:
            raise NameError("wind directions and/or values are null...")
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
            y_data_m = self.list_to_floats(xyData[1])
            fig = pylab.figure()
            pylab.setp(fig, facecolor='w')  # background color
            if self.hasInputFromPort('title'):
                pylab.title(self.getInputFromPort('title'))
            if self.hasInputFromPort('xAxis_label'):
                pylab.xlabel(self.getInputFromPort('xAxis_label'))
            if self.hasInputFromPort('yAxis_label'):
                pylab.ylabel(self.getInputFromPort('yAxis_label'))

            if plot_type == 'date':
                x_data_m = self.list_to_dates(xyData[0])
                pylab.plot_date(x_data_m, y_data_m, xdate=True, marker=marker_type,
                                markerfacecolor=self.facecolor)
                fig.autofmt_xdate()  # pretty-format date axis
            else:
                x_data_m = self.list_to_floats(xyData[0])
                if plot_type == 'scatter':
                    pylab.scatter(x_data_m, y_data_m, marker=marker_type, facecolor=self.facecolor)
                elif plot_type == 'line':
                    pylab.plot(x_data_m, y_data_m, marker=marker_type,
                               linestyle=line_style, markerfacecolor=self.facecolor)
                elif plot_type == 'windrose':
                    fig = self.create_rose(y_data_m, x_data_m)
                else:
                    raise NameError('plot_type %s  is undefined.' % plot_type)

        pylab.get_current_fig_manager().toolbar.hide()
        self.setResult('source', "")


class MultiPlot(ParentPlot):
    """Allows multiple series to be plotted on the same plot.

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
            if type(data_sets) != list:
                data_sets = [data_sets]
        else:
            data_sets = []
        #print "plot:380", data_sets

        fig = pylab.figure()
        pylab.setp(fig, facecolor='w')  # background color
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
            #print "plot:395", x_series
            for key, dataset in enumerate(data_sets):
                if key:  # skip first series (used for X-axis data)
                    marker_number = key - (max_markers * int(key / max_markers)) - 1
                    self.facecolor = self.random_color()

                    # Y AXIS DATA
                    y_data_m = x_data_m = self.list_to_floats(dataset)
                    #print "plot:404", key, marker_number, y_data
                    # X-AXIS DATA
                    if plot_type in ('scatter', 'line'):
                        x_data_m = self.list_to_floats(x_series)

                    if plot_type == 'date':
                        x_data_m = self.list_to_dates(x_series)
                        #print "plot:411", key, marker_number, x_data, x_data_m
                        ax.plot_date(x_data_m, y_data_m, xdate=True,
                                        marker=MARKER[marker_number],
                                        markerfacecolor=self.facecolor)
                        fig.autofmt_xdate()  # pretty-format date axis
                    elif plot_type == 'scatter':
                        ax.scatter(x_data_m, y_data_m, marker=MARKER[marker_number],
                                   facecolor=self.facecolor)
                    elif plot_type == 'line':
                        ax.plot(x_data_m, y_data_m, marker=MARKER[marker_number],
                                linestyle=line_style,
                                markerfacecolor=self.facecolor)
                    else:
                        raise NameError('plot_type %s  is undefined.' % plot_type)

        pylab.get_current_fig_manager().toolbar.hide()
        self.setResult('source', "")


"""
class GroupPlot(ParentPlot):
    Allows multiple series to be plotted on different plots.

    Input ports:
        datapairs:
            a list of lists - each list contains two lists: the first list is
            the X values, and the second list is the Y values.  X-values can be
            numeric or dates, but Y-values must be numeric.
        plotsettings:
            a list of dictionaries of plot settings. Each dictionary is
            associated with a corresponding datapair list, and may include:
             * index: the index of the datapair list item
             * plot: the type of plot (defaults to scatter)
             * title: title that will appear above the plot
             * xAxis_label: the label for the X-axis
             * yAxis_label: the label for the Y-axis

    Output ports:
        source:
            the matplotlib source code for the plot


#Eg. for multiple graphs ...

import matplotlib.pyplot as plt

plt.figure(1)
plt.plot(range(10),range(10))

plt.figure(2)
plt.plot(range(2),range(2))

    """


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
    """matplotlib plot type constants for combobox."""
    _KEY_VALUES = {'scatter': 'scatter', 'line': 'line', 'date(x)': 'date',
                   'windrose': 'windrose'}

MatplotlibPlotTypeComboBox = basic_modules.new_constant('Plot Type',
                                        staticmethod(str),
                                        'scatter',
                                        staticmethod(lambda x: type(x) == str),
                                        MatplotlibPlotTypeComboBoxWidget)


class MatplotlibHistogramTypeComboBoxWidget(ComboBoxWidget):
    """matplotlib histogram type constants for combobox."""
    _KEY_VALUES = {'bar': 'bar', 'step': 'step', 'bar - stacked': 'barstacked',
                   'step - filled': 'stepfilled', }

MatplotlibHistogramTypeComboBox = basic_modules.new_constant('Histogram Type',
                                        staticmethod(str),
                                        'bar',
                                        staticmethod(lambda x: type(x) == str),
                                        MatplotlibHistogramTypeComboBoxWidget)
