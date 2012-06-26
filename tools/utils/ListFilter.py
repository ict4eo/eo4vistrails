# -*- coding: utf-8 -*-
############################################################################
###
### Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
###
### This full package extends VisTrails, providing GIS/Earth Observation
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
"""This module forms part of the eo4vistrails capabilities. It is used to
handle filtering of lists.
"""
# library
import os
import os.path
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin


@RPyCSafeModule()
class ListFilter(ThreadSafeMixin, Module):
    """Accept a list and filter it according to specified filter.

    Input ports:
        list_in:
            a standard VisTrails (Python) list
        subset:
            an optional filter (defaults to "0" -the first item in the list)

    The "subset" specification uses the following syntax:
     *  N: a single integer
     *  N-M: a range of integers
     *  N, M, ...: multiple different single/range values

    Output ports:
        list_out:
            a list containing all filtered items
        string:
            a string'view' of the subsetted list

    """

    """
    _input_ports = [('list_in', '(edu.utah.sci.vistrails.basic:List)'),
                    ('subset', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('string', '(edu.utah.sci.vistrails.basic:String)'),
                    ('list_out', '(edu.utah.sci.vistrails.basic:List)')]
    """

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error with traceback display."""
        import traceback
        traceback.print_exc()
        if error:
            raise ModuleError(self, msg + ' - %s' % str(error))
        else:
            raise ModuleError(self, msg)

    def get_filter(self, items):
        """Create a list of values from numeric ranges defined in a string.

        Accepts:

        A single string, with a specification that uses the following syntax:
         *  N: a single integer; or a single Excel column letter
         *  N-M: a range of integers; or a range of Excel column letters
         *  N, M, ...: multiple different single/range values

        Returns:

         *  A list of integers

        """

        def to_int(index):
            s = 0
            pow = 1
            try:
                return int(index)
            except:
                pass
            for letter in index[::-1]:
                d = int(letter, 36) - 9
                s += pow * d
                pow *= 26
            # excel starts column numeration from 1
            return s

        list = []
        if items:
            try:
                item_list = items.split(',')
                for item in item_list:
                    if '-' in item:
                        _range = item.split('-')
                        _short = [x for x in range(to_int(_range[0]),
                                                   to_int(_range[1]) + 1)]
                        list = list + _short
                    else:
                        list.append(to_int(item))
            except Exception, e:
                self.raiseError('Cannot process output specifications: %s' % str(e))
                return []
        if list:
            return set(list)  # remove duplicates
        else:
            return list  # empty

    def compute(self):
        list_in = self.getInputFromPort('list_in')
        _subset = self.forceGetInputFromPort('subset', None)
        subset_list = self.get_filter(_subset)

        def create_list(list_in, subset_list):
            if list_in:
                if not subset_list:
                    return list_in[0]
                else:
                    result = []
                    for index in subset_list:
                        if index in range(0, len(list_in)):
                            result.append(list_in[index])
                    return result
            return list_in

        def create_string(list_in, subset_list):
            try:
                return str(create_list(list_in, subset_list))
            except:
                return None

        try:
            if 'string' in self.outputPorts:
                self.setResult('string', create_string(list_in, subset_list))
            if 'list_out' in self.outputPorts:
                self.setResult('list_out', create_list(list_in, subset_list))

        except Exception, ex:
            self.raiseError(ex)
        csvfile = None
