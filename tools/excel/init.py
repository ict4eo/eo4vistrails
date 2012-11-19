###########################################################################
##
## Copyright (C) 2012 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation
## ingestion, pre-processing, transformation, analytic and visualisation
## capabilities . Included is the ability to run code transparently in
## OpenNebula cloud environments. There are various software
## dependencies, but all are FOSS.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""This package provides Excel capabilities.
"""


def missing(package_name, module_name):
    print "WARNING: %s package not installed; %s Module disabled" % \
        (package_name, module_name)


def warning(package_name, module_name):
    print "WARNING: %s package not installed; %s Module has reduced \
    functionality" % \
        (package_name, module_name)


def widgetName():
    """ widgetName() -> str
    Return the name of this widget plugin

    """
    return 'Excel-HTML Viewer'


def initialize(*args, **keywords):
    """Called by higher level inits to ensure that registration with
    VisTrails takes place."""
    from core.modules.module_registry import get_module_registry
    import core.requirements
    from core.modules import basic_modules
    from packages.spreadsheet import basic_widgets
    reg = get_module_registry()

    if core.requirements.python_module_exists('xlrd') and \
       core.requirements.python_module_exists('xlwt'):

        from excelcell import ExcelCell  # filename of Vistrails module
        from ExcelUtils import ExcelChopper, ExcelExtractor, ExcelFiller, \
                               ExcelReplacer, ExcelSplitter, ExcelBase, \
                               ExcelMerger, ExcelDirectionComboBox, \
                               ExcelMatchComboBox, ExcelSplitComboBox
        excel_namespace = "tools|excel"

        # abstract modules - drop-down lists
        reg.add_module(ExcelDirectionComboBox,
                       namespace=excel_namespace,
                       abstract=True)
        reg.add_module(ExcelMatchComboBox,
                       namespace=excel_namespace,
                       abstract=True)
        reg.add_module(ExcelSplitComboBox,
                       namespace=excel_namespace,
                       abstract=True)

        # Add ExcelCell
        reg.add_module(ExcelCell,
                       namespace=excel_namespace)
        reg.add_input_port(ExcelCell, "File", basic_modules.File)
        reg.add_input_port(ExcelCell, "Sheets", basic_modules.List)
        reg.add_input_port(ExcelCell, "Location", basic_widgets.CellLocation)
        reg.add_input_port(ExcelCell, "ColumnWidths", basic_modules.List)
        reg.add_input_port(ExcelCell, "References?", basic_modules.Boolean)
        reg.add_output_port(ExcelCell, "HTML File", basic_modules.File)

        # Add other Excel utils
        reg.add_module(ExcelBase,
                       namespace=excel_namespace,
                       abstract=True)
        reg.add_module(ExcelChopper,
                       namespace=excel_namespace)
        reg.add_module(ExcelExtractor,
                       namespace=excel_namespace)
        reg.add_module(ExcelFiller,
                       namespace=excel_namespace)
        reg.add_module(ExcelReplacer,
                       namespace=excel_namespace)
        reg.add_module(ExcelSplitter,
                       namespace=excel_namespace)
        reg.add_module(ExcelMerger,
                       namespace=excel_namespace)

    else:
        missing('xlrd/xlwt', 'excel')
