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
from core.db.locator import FileLocator
from core.console_mode import run
from core import debug


class Runner():

    def __init__(self, keep_active=False, use_cache=False):
        """
        Args:
            keep_active: boolean
                if True, Vistrails must run after executing flows
            use_cache: boolean
                if True, will run VisTrails in caching mode
        """
        # vistrails initialization
        self.gui_app = gui.application
        self.active = keep_active
        self.options = {'useCache': use_cache}
        try:
            vt = self.gui_app.start_application(self.options)
            if vt != 0:
                if self.gui_app.VistrailsApplication:
                    self.gui_app.VistrailsApplication.finishSession()
                sys.exit(vt)
            self.app = self.gui_app.VistrailsApplication()
        except SystemExit, e:
            if self.gui_app.VistrailsApplication:
                self.gui_app.VistrailsApplication.finishSession()
            sys.exit(e)
        except Exception, e:
            if self.gui_app.VistrailsApplication:
                self.gui_app.VistrailsApplication.finishSession()
            print "Uncaught exception on initialization: %s" % e
            import traceback
            traceback.print_exc()
            sys.exit(255)

    def run_flow(self, workflow, version, aliases=None, path=None,
            update=False):
        """Run a workflow version located at a specified path.

        Args:
            workflow: string
            version: string
            aliases: dictionary
                name:value pairs for workflow aliases
            path: string
                if not supplied, use current directory
            update: boolean
                True if you want the log of this execution to be stored
                in the vistrail file
        """
        # api must be imported after vistrails initialization
        import api
        location = path or os.getcwd()
        flow = os.path.join(location, workflow)
        #print "102 Running %s" % (flow)
        locator = FileLocator(os.path.abspath(flow))
        work_list = [(locator, version)]
        parameters = ''
        for key, item in enumerate(aliases.items()):
            parameters = parameters + '%s=%s' % (item[0], item[1])
            if key + 1 < len(aliases):
                parameters = parameters + '$&$'
        errs = run(work_list, parameters=parameters, update_vistrail=update)
        if len(errs) > 0:
            for err in errs:
                debug.critical("Error in %s:%s:%s -- %s" % err)

    '''
    def run(self, workflow, version, aliases=None, path=None):
        """Run a workflow version located at a specified path.

        Args:
            workflow: string
            version: string
            aliases: dictionary
                name:value pairs forr workflow aliases
            path: string
                if not supplied, use current directory
        """
        # api must be imported after vistrails initialization
        import api
        location = path or os.getcwd()
        flow = os.path.join(location, workflow)
        #print "92 Running %s" % (flow)
        api.open_vistrail_from_file(flow)
        #print "94   versions:", api.get_available_versions()
        api.select_version(version)
        controller = api.get_current_controller()
        try:
            controller.execute_current_workflow(custom_aliases=aliases)
        except RuntimeError:
            print "Workflow %s faied..." % flow
    '''