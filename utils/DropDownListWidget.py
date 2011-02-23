from core.modules.constant_configuration import ConstantWidgetMixin
from PyQt4 import QtCore, QtGui

class ComboBoxWidget(QtGui.QComboBox, ConstantWidgetMixin):
    '''Subclass this class to make your own combobox widget with its own list
    by setting the value of _values'''
    
    _values = ['please', 'set', 'values']

    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)
        Initializes the line edit with contents
        """
        QtGui.QCheckBox.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        self.addItems(self._values)
        self.connect(self, QtCore.SIGNAL('activated(QString)'),
                     self.onActivated)
        self.setContents(param.strValue)
    
    def contents(self):
        return self.currentText()

    def setContents(self, strValue, silent=True):
        if strValue:
            value = strValue
        else:
            value = self._values[0]
        assert value in self._values
        #self.setCheckState(self._states[self._values.index(value)])
        self.setCurrentIndex(self.findText(value))
        if not silent:
            self.update_parent()
    
    def onActivated(self, text):
        self.setContents(text)
        self.update_parent()
        
    def change_state(self, state):
        self.update_parent()

class LinuxDemoComboBoxWidget(ComboBoxWidget):
    _values = ['Ubuntu', 'Fedora', 'Gentoo']

