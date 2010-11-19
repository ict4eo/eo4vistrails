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
"""This package provides GIS capabilities for eo4vistrails.
In particular, provides PostGIS clients via psycopg2.
This is not a SQL Builder - it assumes you know SQL
and in particular, spatial SQL as provided by PostGIS. 
You will need to write raw sql by hand. Provsions a session
a.k.a. a postgis connection and allows random queries to be
executed against the chosen database. 
"""

identifier = 'za.co.csir.eo4vistrails.geoinf.postgis'
name = 'eo4vistrails.geoinf.postgis'
version = '0.0.1'

def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('psycopg2'):
        raise core.requirements.MissingRequirement('psycopg2')
