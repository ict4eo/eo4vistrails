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
from datetime import datetime
from numpy import array, ma
import random
import time
import types
import urllib
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
    """Provide common routines and data for all plot modules."""

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

    def to_date(self, string, date_format='%Y-%m-%d'):
        """Return a matplotlib date from a string, in the specified format,
        or 'almost zero' if invalid.

        Notes:
         *  Ignores time-zone settings appended with a +  or T because
            datetime.strptime cannot process those "as is".
        """
        if string:
            string = str(string)
            # remove time zone
            if '+' in string:
                dt = string.split('+')
                _date = dt[0]
            elif 'Z' in string:
                dt = string.split('Z')
                _date = dt[0]
            else:
                _date = string
            # change separators to defaults
            if 'T' in _date:
                _date = _date.replace('T', ' ')
            if '/' in _date:
                _date = _date.replace('/', '-')

            try:
                return matplotlib.dates.date2num(datetime.strptime(_date,
                                                                   date_format))
            except ValueError, e:
                raise ModuleError(self, e)
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

    def series(self, list_array):
        """Convert a list into lists of X and Y values ("series")

        If the list only contains single values, these are assumed to be Y values
        and the X values are created from the index values (starting from 1)

        If the list contains tuples, these are assumed to be ordered X,Y values

        If the list contains sublists:
         * if each of these contains a list of tuples, it is converted as above.
         * if each of these contains a list of values, then:
           * the first list is assumed to contain X values, and
           * the second and subsequent lists are assumed to contain Y values

        """

        def listsOnly(list):
            return len(list) == len([x for x in list if isinstance(x, types.ListType)])

        def tuplesOnly(list):
            return len(list) == len([x for x in list if isinstance(x, types.TupleType)])

        def valuesOnly(list):
            return len(list) == len([x for x in list if not (isinstance(x, types.ListType)\
                                                             or isinstance(x, types.TupleType))])

        xs = []
        ys = []

        if listsOnly(list_array):
            for index, sery in enumerate(list_array):
                if tuplesOnly(sery):
                    xs.append([w[0] for w in sery])
                    ys.append([w[1] for w in sery])
                elif valuesOnly(sery):
                    if index > 0:
                        xs.append(list_array[0])
                        ys.append(sery)
                else:
                    pass

        elif tuplesOnly(list_array):
            xs.append([w[0] for w in list_array])
            ys.append([w[1] for w in list_array])

        elif valuesOnly(list_array):
            ys.append(list_array)
            xs.append([index + 1 for index, i in enumerate(list_array)])

        else:
            pass

        return xs, ys

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
        date_format:
            the applicable format for the date values (in date(x) plots)
             * YY = full year (century and year)
             * MM = zero-padded month
             * DD = zero-padded day
             * HH = zero-padded hours
             * MM = zero-padded minutes
             * SS = zero-padded seconds
             * .n = micro-seconds (up to 6 decimal places)
        title:
            an optional title that will appear above the plot
        xAxis_label:
            an optional label for the X-axis (ignored for windrose)
        yAxis_label:
            an optional label for the Y-axis (ignored for windrose)
        line_style:
            the type of line style (defaults to solid)
        marker:
            the type of marker (defaults to square)
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
                    ('date_format', '(za.co.csir.eo4vistrails:Date Format:utils)'),
                    ('title', '(edu.utah.sci.vistrails.basic:String)'),
                    ('xAxis_label', '(edu.utah.sci.vistrails.basic:String)'),
                    ('yAxis_label', '(edu.utah.sci.vistrails.basic:String)'),
                    ('marker', '(za.co.csir.eo4vistrails:Plot Marker:plots)'),
                    ('line_style', '(za.co.csir.eo4vistrails:Plot Line Style:plots)'),
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
        date_format = self.forceGetInputFromPort('date_format', '%Y-%m-%d')
        marker_type = self.forceGetInputFromPort('marker', 's')
        line_style = self.forceGetInputFromPort('line_style', '-')
        if self.hasInputFromPort('facecolor'):
            self.facecolor = self.getInputFromPort('facecolor').tuple
        else:
            self.facecolor = 'r'

        xyData = self.forceGetInputListFromPort('xyData')
        #print "plot:400", xyData
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
                x_data_m = self.list_to_dates(xyData[0], date_format)
                pylab.plot_date(x_data_m, y_data_m, xdate=True,
                                marker=marker_type,
                                markerfacecolor=self.facecolor)
                fig.autofmt_xdate()  # pretty-format date axis
            else:
                x_data_m = self.list_to_floats(xyData[0])
                if plot_type == 'scatter':
                    pylab.scatter(x_data_m, y_data_m, marker=marker_type,
                                  facecolor=self.facecolor)
                elif plot_type == 'line':
                    pylab.plot(x_data_m, y_data_m, marker=marker_type,
                               linestyle=line_style,
                               markerfacecolor=self.facecolor)
                elif plot_type == 'windrose':
                    fig = self.create_rose(y_data_m, x_data_m)
                else:
                    raise NameError('plot_type %s  is undefined.' % plot_type)
        else:
            raise NameError('A %s plot requires exactly two input lists.'\
                            % plot_type)

        pylab.get_current_fig_manager().toolbar.hide()
        self.setResult('source', "")


class MultiPlot(ParentPlot):
    """Allows multiple series to be plotted on the same plot.

    Input ports:
        xyData:
            a data list of X and Y values - X-values can be numeric or dates,
            but Y-values must be numeric.  The list format can be any one of:
             *  [Y0, Y1, Y2 ... Yn]; in this case the X values are created from
                the index values (i.e. 1, 2, 3...)
             *  [[X0, X1, X2 ... Xn], [Y0, Y1, Y2 ... Yn]]
             *  [(X0, Y0), (X1, Y1), (x2, Y2) ... (Xn, Yn)]
             *  [[X0, X1, X2 ... Xn], [Y0, Y1, Y2 ... Yn], [Y0, Y1, Y2 ... Yn]]
                for multiple series, with the *same* set of X values
             *  [[(X0, Y0), (X1, Y1), (x2, Y2) ... (Xn, Yn)],
                [(X0, Y0), (X1, Y1), (x2, Y2) ... (Xn, Yn)]]
                for multiple series, with *differing* sets of X values
        plot:
            the type of plot
        date_format:
            the applicable format for the date values (in date(x) plots)
             * YY = full year (century and year)
             * MM = zero-padded month
             * DD = zero-padded day
             * HH = zero-padded hours
             * MM = zero-padded minutes
             * SS = zero-padded seconds
             * .n = micro-seconds (up to 6 decimal places)
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
    _input_ports = [('xyData', '(edu.utah.sci.vistrails.basic:List)'),
                    ('plot', '(za.co.csir.eo4vistrails:Plot Type:plots)'),
                    ('date_format', '(za.co.csir.eo4vistrails:Date Format:utils)'),
                    ('title', '(edu.utah.sci.vistrails.basic:String)'),
                    ('xAxis_label', '(edu.utah.sci.vistrails.basic:String)'),
                    ('yAxis_label', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

    def compute(self):
        """Compute results."""
        MARKER = ('o', 'd', '*', '+', 's', 'v', 'x',  '>', '<', '^', 'h', )
        line_style = '-'
        plot_type = self.forceGetInputFromPort('plot', 'scatter')
        date_format = self.forceGetInputFromPort('date_format', '%Y-%m-%d')
        if self.hasInputFromPort('xyData'):
            data_sets = self.getInputFromPort('xyData')
            if type(data_sets) != list:
                data_sets = [data_sets]
        else:
            data_sets = []
        #print "plot:498", data_sets

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
            x_series, y_series = self.series(data_sets)
            for key, dataset in enumerate(x_series):
                #print "plot:515 xdata", key, x_series[key]

                # infinite 'loop' through set of available markers
                marker_number = key - (max_markers * int(key / max_markers)) - 1
                self.facecolor = self.random_color()

                # Y AXIS DATA
                y_data_m = self.list_to_floats(y_series[key])
                print "plot:523 ydata", key, y_data_m

                # X-AXIS DATA
                if plot_type in ('scatter', 'line'):
                    x_data_m = self.list_to_floats(x_series[key])
                elif plot_type in ('date'):
                    x_data_m = self.list_to_dates(x_series[key], date_format)
                else:
                    raise NameError('Plot_type %s  is undefined.' % plot_type)
                print "plot:532 ydata", key, x_data_m

                if plot_type == 'date':
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
