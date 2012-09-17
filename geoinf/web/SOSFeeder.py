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
"""This module forms part of the eo4vistrails capabilities. It is used to
handle data feeds to an OGC SOS (including InsertObservation & RegisterSensor)
"""
# library
import os
import os.path
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
# local
from ThreadSafe import ThreadSafeMixin


@RPyCSafeModule()
class SOSFeeder(ThreadSafeMixin, Module):
    """Accept a file, extract data from it, and POST it to a specified SOS.

    Input ports:
        URL:
            the network address of the SOS
        file_in:
            an Excel (.xls format) data file
        configuration:
            an optional configuration dictionary - this will override the
            default settings used to access data from the Excel file
        active:
            a boolean port; if True (default) then incoming data is POSTed
            directly to the SOS

    Output ports:
        POST:
            an XML string; containing data POSTed to the SOS

    """

    """
    _input_ports = [('URL', '(edu.utah.sci.vistrails.basic:String)'),
                    ('file_in', '(edu.utah.sci.vistrails.basic:File)'),
                    ('configuration', '(edu.utah.sci.vistrails.basic:Dictionary)'),
                    ('active', '(edu.utah.sci.vistrails.basic:Boolean)')]
    _output_ports = [('POST', '(edu.utah.sci.vistrails.basic:String)'),]
    """

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error with traceback display."""
        import traceback
        traceback.print_exc()
        if error:
            raise ModuleError(self, msg + ' - %s' % str(error))
        else:
            raise ModuleError(self, msg)

    def compute(self):
        URL = self.getInputFromPort('URL')
        file_in = self.getInputFromPort('file_in')
        _config = self.forceGetInputFromPort('configuration', None)
        active = self.forceGetInputFromPort('active', True)

        try:
            config = self.get_config(_config)
            if 'file_in' in self.outputPorts:
                self.setResult('POST', create_data(config))
            """
            if 'list_out' in self.outputPorts:
                self.setResult('list_out', create_xml())
            """

        except Exception, ex:
            self.raiseError(ex)

    def get_config(self, config=None):
        """Create the configuration needed to read data in from the file."""
        return None

    def create_data(self, config=None):
        """Create the XML for the POST to the SOS, using a Jinja template."""
        return None