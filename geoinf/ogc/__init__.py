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
"""This package provides OGC capabilities for eo4vistrails.
In particular, provides WFS, WCS and SOS clients through 
the owslib (http://gispython.org/owslib) library, and hence 
has a dependency thereupon. owslib is dependent on libxml 
or elementree
"""

identifier = 'za.co.csir.eo4vistrails.geoinf.ogc'
name = 'eo4vistrails.geoinf.ogc'
version = '0.0.1'

def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('owslib'):
        raise core.requirements.MissingRequirement('owslib')
    else:
        from owslib import wfs,  wcs,  sos

