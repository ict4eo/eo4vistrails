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
#"""This full package extends VisTrails, providing GIS/Earth Observation 
#ingestion, pre-processing, transformation, analytic and visualisation 
#capabilities . Included is the abilty to run code transparently in 
#OpenNebula cloud environments.
#"""

from core.modules import module_configure
from core import packagemanager
from core.modules.module_registry import get_module_registry
from core.modules.vistrails_module import Module, NotCacheable, ModuleError
from core.modules import basic_modules

import urllib
import sys


class OneAbstract(NotCacheable, Module):
    """TO DO - add docstring"""
    def __init__(self):
        Module.__init__(self)

    def runcmd(self, operation):
        import paramiko   
        client = paramiko.SSHClient()
        client.load_system_host_keys()  
        self.username = self.getInputFromPort("username")
        self.password = self.getInputFromPort("password")
        self.server = self.getInputFromPort("server")
        client.connect(self.server,username=self.username,password=self.password)
        i,o,e = client.exec_command(operation)
        self.setResult("stdout", o.readlines())
        self.setResult("stderr", e.readlines())

    def compute(self):
        """Vistrails Module Compute, Entry Point Refer, to Vistrails Docs"""
        pass


class OneCmd(OneAbstract):
    """TO DO - add docstring"""
    # This constructor is strictly unnecessary. However, some modules
    # might want to initialize per-object data. When implementing your
    # own constructor, remember that it must not take any extra
    # parameters.
    def __init__(self):
        OneAbstract.__init__(self)

    def compute(self):
        """Vistrails Module Compute, Entry Point Refer, to Vistrails Docs"""
        operation = self.getInputFromPort("operation")
        self.runcmd(operation)


class OneVM_List(OneAbstract):
    """TO DO - add docstring"""
    def __init__(self):
        OneAbstract.__init__(self)

    def compute(self):
        """Vistrails Module Compute, Entry Point Refer, to Vistrails Docs"""
        self.runcmd("source .one-env; onevm list")
        for i in t:
            if i.find('missr')>=0:
                int(i[0:i.find('missr')])


################################################################################
# RPyC
#
# A VisTrails name, globals, locals, fromlist, level))
# Module.  For this class to be executable, it must define a method
# compute(self) that will perform the appropriate computations and set
# the results.
#
# Extra helper methods can be defined, as usual. In this case, we're
# using a helper method op(self, v1, v2) that performs the right
# operations.
################################################################################
from core.modules.module_configure import StandardModuleConfigurationWidget
class RPyCConfigurationWidget(StandardModuleConfigurationWidget):
    """makes use of code style from TupleConfigurationWidget"""
    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, parent)
        #initialise the setup necessary for all geoinf widgets that follow
        self.setWindowTitle('RPyC Configuration Window ')
        self.setToolTip("Setup RPyC Configuration paramaters for working with cloud")
        self.createTabs()
        self.createButtons()
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().addLayout(self.tabLayout)
        self.layout().addLayout(self.buttonLayout)

    def updateVistrail(self):
        """TO DO - add docstring"""
        msg = "Must implement updateVistrail in subclass"
        raise VistrailsInternalError(msg)

    def createTabs(self):
        """ createTabs() -> None
        create and polulate with widgets the necessary 
        tabs for spatial and temporal paramaterisation
        
        """
        self.tabs = SpatioTemporalConfigurationWidgetTabs()
        self.spatial_widget = SpatialWidget()
        self.temporal_widget = TemporalWidget()
        self.tabs.addTab(self.spatial_widget, "")
        self.tabs.addTab(self.temporal_widget, "")
        
        self.tabs.setTabText(self.tabs.indexOf(self.spatial_widget), QtGui.QApplication.translate("SpatialTemporalConfigurationWidget", "Bounding Coordinates", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabToolTip(self.tabs.indexOf(self.spatial_widget), QtGui.QApplication.translate("SpatialTemporalConfigurationWidget", "Gather coordinates of a bounding box, or in the case of GRASS, a location", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(self.tabs.indexOf(self.temporal_widget), QtGui.QApplication.translate("SpatialTemporalConfigurationWidget", "Temporal Bounds and Intervals", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabToolTip(self.tabs.indexOf(self.temporal_widget), QtGui.QApplication.translate("SpatialTemporalConfigurationWidget", "Choose and set temporal bounds and interval paramaters", None, QtGui.QApplication.UnicodeUTF8))       
        
        self.tabLayout = QtGui.QHBoxLayout()
        self.tabLayout.addWidget(self.tabs)        
        self.tabs.setCurrentIndex(0)
        self.tabs.setVisible(True)

    def createButtons(self):
        """ createButtons() -> None
        Create and connect signals to Ok & Cancel button
        
        """
        self.buttonLayout = QtGui.QHBoxLayout()
        #self.buttonLayout.setGeometry(QtCore.QRect(10, 765, 980, 32))
        self.buttonLayout.setGeometry(QtCore.QRect(300, 500, 780, 680))
        self.buttonLayout.setMargin(5)
        self.cancelButton = QtGui.QPushButton('&Cancel', self)
        self.cancelButton.setAutoDefault(False)
        self.cancelButton.setShortcut('Esc')
        self.cancelButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.cancelButton)  
        self.okButton = QtGui.QPushButton('&OK', self)
        self.okButton.setAutoDefault(False)
        self.okButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.okButton)
        self.connect(self.okButton, QtCore.SIGNAL('clicked(bool)'),
                     self.okTriggered)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked(bool)'),
                     self.close)        

    def sizeHint(self):
        """ sizeHint() -> QSize
        Return the recommended size of the configuration window
        
        """
        return QtCore.QSize(800, 600)

    def okTriggered(self, checked = False):
        """ okTriggered(checked: bool) -> None
        Update vistrail controller and module when the user click Ok
        
        """
        if self.updateVistrail():
            self.emit(QtCore.SIGNAL('doneConfigure()'))
            self.close()



class RPyCDiscover(NotCacheable, Module):
    """
    RPyCDiscover is a Module that allow one to discover RPyC
    servers
    """
    # This constructor is strictly unnecessary. However, some modules
    # might want to initialize per-object data. When implementing your
    # own constructor, remember that it must not take any extra
    # parameters.
    def __init__(self):
        Module.__init__(self)
        
    def getSlaves(self):
        import rpyc
        discoveredSlavesTuple = list(rpyc.discover("slave"))
        discoveredSlaves = []
        for slave in discoveredSlavesTuple:
            discoveredSlaves.append(list(slave))
        return discoveredSlaves
        

    def compute(self):
        """Vistrails Module Compute, Entry Point Refer, to Vistrails Docs"""
        self.setResult("rpycslaves", self.getSlaves())

class RPyC(NotCacheable, Module):
    """
    RPyC is a Module that executes an arbitrary piece of Python code remotely.
    TODO: If you want a PythonSource execution to fail, call fail(error_message).
    TODO: If you want a PythonSource execution to be cached, call cache_this().
    """
      
    # This constructor is strictly unnecessary. However, some modules
    # might want to initialize per-object data. When implementing your
    # own constructor, remember that it must not take any extra
    # parameters.
    def __init__(self):
        Module.__init__(self)

    def run_code(self, code_str, use_input=False, use_output=False):
        """
        run_code runs a piece of code as a VisTrails module.
        use_input and use_output control whether to use the inputport
        and output port dictionary as local variables inside the
        execution.
        """
        import rpyc

        def fail(msg):
            raise ModuleError(self, msg)

        def cache_this():
            self.is_cacheable = lambda *args, **kwargs: True
        
        if type(self.getInputFromPort('rpycslave')) == list:
            conn = rpyc.classic.connect(self.getInputFromPort('rpycslave')[0][0],self.getInputFromPort('rpycslave')[0][1])
        else:
            conn = rpyc.classic.connect(self.getInputFromPort('rpycslave')[0],self.getInputFromPort('rpycslave')[1])

        if use_input:
            inputDict = dict([(k, self.getInputFromPort(k)) for k in self.inputPorts])
            conn.namespace.update(inputDict)
        
        if use_output:
            outputDict = dict([(k, None) for k in self.outputPorts])
            conn.namespace.update(outputDict)

        _m = packagemanager.get_package_manager()
        reg = get_module_registry()
        conn.namespace.update({'fail': fail,
                        'package_manager': _m,
                        'cache_this': cache_this,
                        'registry': reg,
                        'self': self})
        del conn.namespace['source']

        #TODO: changed to demo that this is in the cloud!!!!
        #conn.modules.sys.stdout = sys.stdout
        conn.execute(code_str)
        #exec code_str in locals_, locals_
        if use_output:
            for k in outputDict.iterkeys():
                if conn.namespace[k] != None:
                    self.setResult(k, conn.namespace[k])

    def compute(self):
        """
        Vistrails Module Compute, Entry Point Refer, to Vistrails Docs
        """
        s = basic_modules.urllib.unquote(
            str(self.forceGetInputFromPort('source', ''))
        )
        self.run_code(s, use_input=True, use_output=True)
