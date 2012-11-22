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
"""This module is the called by higher level inits to ensure that registration
with VisTrails takes place
"""

from core.modules.module_registry import get_module_registry


def registerControl(module):
    """Register the control modules so that all have the same style & shape."""

    reg = get_module_registry()
    utils_namespace = "tools|utils"
    reg.add_module(module,
                   moduleRightFringe=[(0.0, 0.0), (0.25, 0.5), (0.0, 1.0)],
                   moduleLeftFringe=[(0.0, 0.0), (0.0, 1.0)],
                   namespace=utils_namespace)


def initialize(*args, **keywords):
    from core.modules import basic_modules
    from packages.spreadsheet import basic_widgets
    from core.modules.vistrails_module import Module

    import DropDownListWidget
    from Array import NDArrayEO
    from Experiment import Timer
    from ListFilter import ListFilter
    from ListCell import ListCell
    from Random import Random
    from session import Session
    from ThreadSafe import Fork, ThreadTestModule, ThreadSafeFold, \
        ThreadSafeMap

    reg = get_module_registry()
    utils_namespace = "tools|utils"
    utils_test_namespace = "tools|utils|tests"

    # =========================================================================
    # Abstract Modules - these MUST appear FIRST
    # =========================================================================

    reg.add_module(Session,
                   namespace=utils_namespace,
                   abstract=True)

    # =========================================================================
    # ComboBox definitions
    # =========================================================================

    # LinuxComboBox
    LinuxDemoComboBox = basic_modules.new_constant('LinuxDemoComboBox',
                                    staticmethod(eval),
                                    (1, 1),
                                    staticmethod(lambda x: type(x) == tuple),
                                    DropDownListWidget.LinuxDemoComboBoxWidget)

    reg.add_module(LinuxDemoComboBox,
                   namespace=utils_test_namespace)

    # DateFormatComboBox
    DateFormatComboBox = basic_modules.new_constant('Date Format',
                                    staticmethod(str),
                                    's',
                                    staticmethod(lambda x: type(x) == str),
                                    DropDownListWidget.DateFormatComboBoxWidget)

    reg.add_module(DateFormatComboBox,
                   namespace=utils_namespace,
                   abstract=True)

    # =========================================================================
    # Standard Modules - Ports defined here
    # =========================================================================

    # Experiment
    reg.add_module(Timer,
               name="WorkflowTimer",
               namespace=utils_namespace)

    # Fork
    reg.add_module(Fork,
                   namespace=utils_namespace)
    reg.add_input_port(
        Fork,
        'modules',
        basic_modules.Module)

    # Add ListCell
    reg.add_module(ListCell,
                   namespace=utils_namespace)
    reg.add_input_port(ListCell, "List", basic_modules.List)
    #reg.add_input_port(ListCell, "File", basic_modules.File)
    reg.add_input_port(ListCell, "Location", basic_widgets.CellLocation)
    reg.add_input_port(ListCell, "LineNumber?", basic_modules.Boolean)
    reg.add_output_port(ListCell, "HTML File", basic_modules.File)

    # ListFilter
    reg.add_module(ListFilter,
                   namespace=utils_namespace)
    reg.add_input_port(
        ListFilter,
        'list_in',
        basic_modules.List)
    reg.add_input_port(
        ListFilter,
        'subset',
        basic_modules.String)
    reg.add_output_port(
        ListFilter,
        'string',
        (basic_modules.String, 'String representation of sub-setted list'))
    reg.add_output_port(
        ListFilter,
        'list_out',
        (basic_modules.List, 'sub-setted list'))

    # NDArray
    reg.add_module(NDArrayEO,
                   name="EONumpyArray",
                   namespace=utils_namespace,
                   abstract=True)
    reg.add_output_port(
        NDArrayEO,
        "self",
        (NDArrayEO, 'self'))

    # ThreadTest
    reg.add_module(ThreadTestModule,
                   namespace=utils_test_namespace)
    reg.add_input_port(
        ThreadTestModule,
        'someModuleAboveMe',
        basic_modules.Module)

    # =========================================================================
    # Control Flow Modules -
    # =========================================================================

    registerControl(ThreadSafeFold)
    registerControl(ThreadSafeMap)

    reg.add_input_port(ThreadSafeFold, 'FunctionPort', (Module, ""))
    reg.add_input_port(ThreadSafeFold, 'InputList', (basic_modules.List, ""))
    reg.add_input_port(ThreadSafeFold, 'InputPort', (basic_modules.List, ""))
    reg.add_input_port(ThreadSafeFold, 'OutputPort', (basic_modules.String, ""))
    reg.add_output_port(ThreadSafeFold, 'Result', (basic_modules.Variant, ""))

    # =========================================================================
    # Other Modules - without ports OR with locally defined ports
    # =========================================================================

    reg.add_module(Random,
                   namespace=utils_namespace)
