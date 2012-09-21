###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation
## ingestion, pre-processing, transformation, analytic and visualisation
## capabilities . Included is the abilty to run code transparently in
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
"""This package provides Excel capabilities for eo4vistrails.
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

    if core.requirements.python_module_exists('xlrd'):
        from excelcell import ExcelCell  # filename of Vistrails module
        excel_namespace = "tools|excel"
        #Add PySAL
        reg.add_module(ExcelCell,
                       namespace=excel_namespace)
        reg.add_input_port(ExcelCell, "Location", basic_widgets.CellLocation)
        reg.add_input_port(ExcelCell, "File", basic_modules.File)
    else:
        missing('xlrd', 'excel')
