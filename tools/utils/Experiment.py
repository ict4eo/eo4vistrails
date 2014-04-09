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
# -*- coding: utf-8 -*-
"""TODO  Add documentation to this module.
"""
#Created on Thu Aug 25 09:46:42 2011 @author: tvzyl

from core.modules.vistrails_module import Module, NotCacheable
from core.upgradeworkflow import UpgradeWorkflowHandler
from time import time


class Timer(NotCacheable, Module):
    """ Container class for the random class """

    _input_ports = [('file sink', '(edu.utah.sci.vistrails.basic:File)'),
                    ('start flow', '(edu.utah.sci.vistrails.basic:Module)'),
                    ('input 1', '(edu.utah.sci.vistrails.basic:Module)'),
                    ('input 2', '(edu.utah.sci.vistrails.basic:Module)'),
                    ('input 3', '(edu.utah.sci.vistrails.basic:Module)'),
                    ('input 4', '(edu.utah.sci.vistrails.basic:Module)'),
                    ('input 5', '(edu.utah.sci.vistrails.basic:Module)'),
                    ('input 6', '(edu.utah.sci.vistrails.basic:Module)'),
                    ('input 7', '(edu.utah.sci.vistrails.basic:Module)'),
                    ('input 8', '(edu.utah.sci.vistrails.basic:Module)'),
                    ('input names', '(edu.utah.sci.vistrails.basic:List)')
                    ]

    _output_ports = [('total time', '(edu.utah.sci.vistrails.basic:Float)'),
                     #('header', '(edu.utah.sci.vistrails.basic:String)'),
                     #('record', '(edu.utah.sci.vistrails.basic:String)'),
                     ('report', '(edu.utah.sci.vistrails.basic:String)')
                     ]

    def __init__(self):
        Module.__init__(self)
        self.start_time = 0

    def handle_module_upgrade_request(self, controller, module_id, pipeline):
        module_remap = {'Workflow Timer':
                        [(None, '0.1.3', 'WorkflowTimer', {})],
                        }
        return UpgradeWorkflowHandler.remap_module(controller, module_id,
                                                   pipeline, module_remap)

    def update(self):
        self.start_time = time()
        Module.update(self)

    def compute(self):
        end_time = time()
        total_time = end_time - self.start_time

        file_sink = self.forceGetInputFromPort('file sink', None)

        values = []
        for i in range(8):
            value = self.forceGetInputFromPort('input %s' % (i + 1), None)
            if value:
                values.append(value)

        names = self.forceGetInputFromPort('input names')
        names = names + ['_?_' for _ in xrange(len(values) - len(names))] + ['total_time']

        report = ""
        csv_report = ""

        for value, name in zip(values, names[0:8]):
            if value:
                report += "%s:%s " % (name, value)
                csv_report += "%s," % value
        report += "total_time:%s" % total_time
        csv_report += "%s\n" % total_time

        if file_sink:
            try:
                file_sink_file = open(file_sink.name, "r+")
            except IOError:
                file_sink_file = open(file_sink.name, "w")
                file_sink_file.write(",".join(names[0:8]) + "\n")
            file_sink_file.seek(0, 2)
            file_sink_file.write(csv_report)
            file_sink_file.close()
        self.setResult("total time", total_time)
        self.setResult("report", report)
