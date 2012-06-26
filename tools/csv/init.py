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


def initialize(*args, **keywords):
    from core.modules import basic_modules
    from core.modules.vistrails_module import Module

    from CsvUtils import CsvWriter, CsvReader, CsvFilter

    reg = get_module_registry()
    csv_namespace = "tools|csv"

    # =========================================================================
    # Abstract Modules - these MUST appear FIRST
    # =========================================================================

    # =========================================================================
    # ComboBox definitions
    # =========================================================================

    # =========================================================================
    # Standard Modules - Ports defined here
    # =========================================================================

    # =========================================================================
    # Other Modules - without ports OR with locally defined ports
    # =========================================================================

    reg.add_module(CsvWriter,
                   namespace=csv_namespace)

    reg.add_module(CsvReader,
                   namespace=csv_namespace)

    reg.add_module(CsvFilter,
                   namespace=csv_namespace)
