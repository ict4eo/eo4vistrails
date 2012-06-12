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

NOTE: This set of tests is designed to be run from the commandline, while
working in the directory containing these workflows.
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

def local_test(file_in, file_out, flow, version):
    if file_in:
        file_in = os.path.join(path, file_in)
    file_out = os.path.join(path, file_out)
    aliases={'file_out': file_out, 'file_in': file_in}
    if os.path.isfile(file_out):
        os.remove(file_out)
    print "file_out", file_out
    r.run_flow(flow, version, aliases)
    assert(os.path.isfile(file_out))

# SOS
local_test(None, 'data_out/sos_out.xml', 'sos.vt', 'TOFILE')
# NETCDF - will not work unless run in non-cached mode
local_test(None, 'data_out/netcdf_array.txt', 'netcdf.vt', 'TEST',)
# stringtofile
local_test(None, 'data_out/string_out.txt', 'stringtofile.vt', 'TEST')
# layerwriter
local_test('data_in/alaska.shp', 'data_out/shape_out.shp',
           'layerwriter.vt', 'TEST')
# WFS
local_test(None, 'data_out/wfs_out.xml', 'wfs.vt', 'TEST')
# x
#local_test(None, )

"""
# example without using local_test...
# layerwriter
file_in = os.path.join(path, 'data_in/alaska.shp')
file_out = os.path.join(path, 'data_out/shape_out.shp')
if os.path.isfile(file_out):
    os.remove(file_out)
print "file_out", file_out
r.run_flow('layerwriter.vt', 'TEST', aliases={'file_out': file_out,
                                               'file_in': file_in})
assert(os.path.isfile(file_out))
"""