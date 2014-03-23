###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation
## ingestion, pre-processing, transformation, analytic and visualisation
## capabilities . Included is the ability to run code transparently in
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
"""This module provides general OGC (Open Geospatial Consortium) Web Service
selection widgets for configuring geoinf.web modules.

This refers primarily to GetCapabilities requests
"""
# library
# third-party
from PyQt4 import QtCore, QtGui
# vistrails
from core import debug
from gui.modules.module_configure import StandardModuleConfigurationWidget
from core.modules.module_registry import get_module_registry
from core.utils import PortAlreadyExists
# eo4vistrails


class Port():
    """TODO - write docstring
    """

    #see: /vistrails/core/vistrail/port_spec.py
    def __init__(self, id=None, name=None,
                 sigstring='edu.utah.sci.vistrails.basic:String',
                 type='input', sort_key=-1):
        self.id = str(id)
        self.name = str(name)
        self.sigstring = str(sigstring)
        self.type = type
        self.sort_key = sort_key

    def value(self):
        """Create a tuple-form of a port, for use by Vistrails module"""
        return ((self.id, '(' + self.sigstring + ')', self.sort_key))


class PortConfigurationWidget(StandardModuleConfigurationWidget):
    """Configuration widget for specifying any number of input (output) ports
    and the type of each port.
    
    The module composes (or decomposes) a tuple of inputs as a result.
    
    When subclassing StandardModuleConfigurationWidget, there are
    only two things we need to care about:

    1. The builder will provide the VistrailController (through the
       constructor) associated with the pipeline the module is in. The
       configuration widget can use the controller to change the
       current vistrail such as delete connections, add/delete module
       port...

    2. The builder also provide the current Module object (through the
       constructor) of the module. This is the instance of the module
       in the pipeline. Changes to this Module object usually will not
       result a new version in the current Vistrail. Such changes are
       change the visibility of input/output ports on the builder,
       change module color.

       Each module has a local set of input and output ports that may
       change, unlike those stored by the global registry. The same
       module can have different types of input ports at two different
       time in the same vistrail.

    The rest of the widget will be just like a regular Qt widget.
    """
    def __init__(self, module, controller, parent=None):
        """ PortConfigurationWidget(module: Module,
                                         controller: VistrailController,
                                         parent: QWidget)
                                         -> PortConfigurationWidget

        Let StandardModuleConfigurationWidget constructor store the
        controller/module object from the builder and set up the
        configuration widget.

        After StandardModuleConfigurationWidget constructor, all of
        these will be available:
        * self.module : the Module object in the pipeline
        * self.module_descriptor: the descriptor for the type
                                    registered in the registry
        * self.controller: the current vistrail controller

        """
        StandardModuleConfigurationWidget.__init__(self, module,
                                                   controller, parent)
        self.module = module
        self.ports = []

    def createButtons(self):
        """ createButtons() -> None
        Create and connect signals to Ok & Cancel button

        """
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setMargin(5)
        self.okButton = QtGui.QPushButton('&OK', self)
        self.okButton.setAutoDefault(False)
        self.okButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton('&Cancel', self)
        self.cancelButton.setAutoDefault(False)
        self.cancelButton.setShortcut('Esc')
        self.cancelButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.cancelButton)
        self.layout().addLayout(self.buttonLayout)
        self.connect(self.okButton, QtCore.SIGNAL('clicked(bool)'),
                     self.okTriggered)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked(bool)'),
                     self.close)

    def sizeHint(self):
        """ sizeHint() -> QSize
        Return the recommended size of the configuration window

        """
        return QtCore.QSize(512, 256)

    def okTriggered(self, checked=False):
        """ okTriggered(checked: bool) -> None
        Update vistrail controller and module when the user click Ok

        """
        if self.updateVistrail():
            self.emit(QtCore.SIGNAL('doneConfigure()'))
            self.close()

    def getRegistryPorts(self, registry, type):
        """Return list of tuples containing port types and descriptors

        Example:
            from core.modules.module_registry import get_module_registry
            registry = get_module_registry()
            port_name_sigstring = self.getRegistryPorts(registry, 'input')
        """
        if not registry:
            return []
        if type == 'input':
            getter = registry.destination_ports_from_descriptor
        elif type == 'output':
            getter = registry.source_ports_from_descriptor
        else:
            raise VistrailsInternalError("Unrecognized port type '%s'", type)
        return [(p.name, p.sigstring) for p in getter(self.module_descriptor)]

    def registryChanges(self, old_ports, new_ports):
        deleted_ports = [p for p in old_ports if p not in new_ports]
        added_ports = [p for p in new_ports if p not in old_ports]
        return (deleted_ports, added_ports)

    def getPortDiff(self, p_type):
        if p_type == 'input':
            old_ports = [(p.name, p.sigstring, p.sort_key)
                         for p in self.module.input_port_specs]
        elif p_type == 'output':
            old_ports = [(p.name, p.sigstring, p.sort_key)
                         for p in self.module.output_port_specs]
        else:
            old_ports = []
        # old_ports = self.getRegistryPorts(self.module.registry, p_type)
        new_ports = self.getPorts(type=p_type)
        (deleted_ports, added_ports) = \
            self.registryChanges(old_ports, new_ports)
        deleted_ports = [(p_type,) + p for p in deleted_ports]
        added_ports = [(p_type,) + p for p in added_ports]
        return (deleted_ports, added_ports)

    def getPorts(self, type='input'):
        port_list = []
        for p in self.ports:
            if p.type == type or not type:
                port_list.append(p.value())
        #print 'getPorts for type', type, port_list
        return port_list

    def addPort(self, port):
        #print 'port:',port
        self.ports.append(port)

    def updateVistrail(self):
        """Cause the added/deleted ports to be set for this instance of the
        Module.

        """
        deleted_ports = []
        added_ports = []
        (input_deleted_ports, input_added_ports) = self.getPortDiff('input')
        deleted_ports.extend(input_deleted_ports)
        added_ports.extend(input_added_ports)
        (output_deleted_ports, output_added_ports) = self.getPortDiff('output')
        deleted_ports.extend(output_deleted_ports)
        added_ports.extend(output_added_ports)

        try:
            self.controller.update_ports(self.module.id, deleted_ports, added_ports)

        except PortAlreadyExists, e:
            debug.critical('Port Already Exists %s' % str(e))
            return False
        return True
