# library
# third party
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# vistrails
from core.modules.vistrails_module import Module, ModuleError
from gui.modules.module_configure import StandardModuleConfigurationWidget

version = "0.9.0"
name = "Divide"
identifier = "edu.utah.sci.vistrails.divide"


class Divide(Module):
    """Divide two floating point numbers."""

    def __init__(self):
        Module.__init__(self)

    def compute(self):
        arg1 = self.getInputFromPort("arg1")
        arg2 = self.getInputFromPort("arg2")
        if arg2 == 0.0:
            raise ModuleError(self, "Division by zero")
        self.setResult("result", arg1 / arg2)

    _input_ports = [('arg1', '(edu.utah.sci.vistrails.basic:Float)'),\
                    ('arg2', '(edu.utah.sci.vistrails.basic:Float)')]
    _output_ports = [('result', '(edu.utah.sci.vistrails.basic:Float)'),
                     ('op', '(edu.utah.sci.vistrails.basic:String)')]


#_modules = [Divide]


class DivideConfigurationWidget(StandardModuleConfigurationWidget):
    """A widget to configure the  Divide Module."""

    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, parent)
        self.title = module.name
        #self.module = module
        self.setObjectName("DivideWidget")
        self.parent_widget = module
        self.create_config_window()

    def create_config_window(self):
        """TO DO - add docstring"""
        self.setWindowTitle(self.title)
        self.setMinimumSize(800, 850)

        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        #group box for organisation
        self.crsGroupBox = QtGui.QGroupBox("Define Inputs")
        self.crsLayout = QtGui.QHBoxLayout()
        self.crsGroupBox.setLayout(self.crsLayout)

        self.crsChooseButton = QtGui.QPushButton('&Choose Option')
        self.crsLayout.addWidget(self.crsChooseButton)

        #ok/cancel buttons
        self.finishGroupBox = QtGui.QGroupBox("Finish")
        self.buttonLayout = QtGui.QHBoxLayout()
        self.finishGroupBox.setLayout(self.buttonLayout)

        self.buttonLayout.setGeometry(QtCore.QRect(300, 500, 780, 680))
        self.buttonLayout.setMargin(5)
        self.cancelButton = QtGui.QPushButton('&Cancel', self)
        self.cancelButton.setAutoDefault(False)
        self.cancelButton.setShortcut('Esc')
        self.buttonLayout.addStretch(1)  # force buttons to the right
        self.buttonLayout.addWidget(self.cancelButton)
        self.okButton = QtGui.QPushButton('&OK', self)
        self.okButton.setAutoDefault(False)
        self.buttonLayout.addWidget(self.okButton)
        self.connect(self.okButton,
                     QtCore.SIGNAL('clicked(bool)'),
                     self.okTriggered)
        self.connect(self.cancelButton,
                     QtCore.SIGNAL('clicked(bool)'),
                     self.close)

        #add layouts to main layout
        self.mainLayout.addWidget(self.crsGroupBox)
        self.mainLayout.addWidget(self.finishGroupBox)

        # set signals
        self.connect(self.crsChooseButton,
                     QtCore.SIGNAL('clicked(bool)'),
                     self.getOption)

    def getOption(self):
        pass

    def okTriggered(self):
        foo = 1.0
        #self.controller.update_ports_and_functions(self.module.id, [], [], functions)
        # NB -  functions = array of port tuples: ("portname", array_of_port_values)
        #       port_value MUST be wrapped in an array, as Vistrails allows for
        #       possibility of multiple inputs to a p
#        self.controller.update_ports_and_functions(
#                self.module.id, [], [], [("arg1", [foo]), ("arg2", [foo])])
        self.close()


def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry

    reg = get_module_registry()
    reg.add_module(Divide,
                   configureWidgetType=DivideConfigurationWidget,
                   namespace='divide')
