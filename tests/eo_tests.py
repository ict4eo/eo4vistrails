# -*- coding: utf-8 -*-
############################################################################
###
### Copyright (C) 2012 CSIR Meraka Institute. All rights reserved.
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
"""This module runs test workflows to validate changes in other modules.
"""
#History
#Derek Hohls, 6 June 2012, Version 1.0

# library
import os
# local
from runner import Runner

# initialize
r = Runner()
path = os.getcwd()

# SOS
file_out = os.path.join(path, 'sos_output.xml')
if os.path.isfile(file_out):
    os.remove(file_out)
r.run('sos.vt', 'TOFILE', aliases={'file_out': file_out})
assert(os.path.isfile(file_out))

# NETCDF - will not work unless run in non-cached mode
file_out = os.path.join(path, 'netcdf_array.txt')
if os.path.isfile(file_out):
    os.remove(file_out)
r.run('netcdf.vt', 'TEST', aliases={'file_out': file_out})
assert(os.path.isfile(file_out))



