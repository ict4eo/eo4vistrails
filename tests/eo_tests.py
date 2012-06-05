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
"""This module stores the controller to run workflows to validate changes in
other modules.
"""
#History
#Derek Hohls, 5 June 2012, Version 1.0

# library
import sys
import os
# third party
from PyQt4 import QtGui
# loal
from settings import VISTRAILS_HOME
# vistrails
sys.path.append(VISTRAILS_HOME)
import core.requirements
core.requirements.check_pyqt4()
import gui.application


def run(workflow, version, path=None):
    """Run a workflow version located at a specified path."""
    location = path or os.getcwd()
    flow = os.path.join(location, workflow)
    print "Running ", flow
    api.open_vistrail_from_file(flow)
    # execute a version of a workflow - go through the controller
    #print "   versions:", api.get_available_versions()
    api.select_version(version)
    try:
        api.get_current_controller().execute_current_workflow()
    except RuntimeError:
        print "Workflow %s faied..." % flow

# vistrails initialization
try:
    vt = gui.application.start_application()
    if vt != 0:
        if gui.application.VistrailsApplication:
            gui.application.VistrailsApplication.finishSession()
        sys.exit(vt)
    app = gui.application.VistrailsApplication()
except SystemExit, e:
    if gui.application.VistrailsApplication:
        gui.application.VistrailsApplication.finishSession()
    sys.exit(e)
except Exception, e:
    if gui.application.VistrailsApplication:
        gui.application.VistrailsApplication.finishSession()
    print "Uncaught exception on initialization: %s" % e
    import traceback
    traceback.print_exc()
    sys.exit(255)
# api must be imported after vistrails initialization
import api

# local workflow tests
#run('netcdf.vt', 'TEST -a"filename=foo"')   ERROR - cannt add alias like this!
run('netcdf.vt', 'TEST')
run('sos.vt', 'TOFILE')

# uncomment the line below if Vistrails must run after executing flows
#vt = app.exec_()
gui.application.stop_application()
sys.exit(vt)
