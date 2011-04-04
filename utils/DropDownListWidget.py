from core.modules.constant_configuration import ConstantWidgetMixin
from PyQt4 import QtCore, QtGui

class ComboBoxWidget(QtGui.QComboBox, ConstantWidgetMixin):
    '''
    Subclass this class to make your own combobox widget with its own list
    by setting the value of _KEY_VALUES or by redefing getKeyValues()
    keys must be strings in the dict
    '''
    
    _KEY_VALUES = {'please':'1', 'set':'2', 'values':'3'}
    default = ''

    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)
        Initializes the line edit with contents
        """
        QtGui.QComboBox.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        
        self.addItems(self.getKeyValues().keys())
        self.connect(self, QtCore.SIGNAL('activated(QString)'),
                     self.onActivated)
        
        if param.strValue == '':
            checkstr = str(self.default)
        else:
            checkstr = param.strValue    
        
        print "1->", param.strValue
        for (k,v) in self.getKeyValues().items():
            print "2->", k, v
            if str(v) == checkstr:
                break
        
        self.setContents(k)
    
    def getKeyValues(self):
        return self._KEY_VALUES
    
    def contents(self):
        return self.getKeyValues()[str(self.currentText())]

    def setContents(self, inKey, silent=True):
        keyvalues = self.getKeyValues()
        if inKey:
            value = keyvalues[str(inKey)]
        else:
            value = keyvalues.values()[0]
        
        assert value in keyvalues.values()
        
        for (k,v) in keyvalues.items():
            if str(v) == str(value):
                break
        
        self.setCurrentIndex(self.findText(k))
        if not silent:
            self.update_parent()
    
    def onActivated(self, text):
        self.setContents(text)
        self.update_parent()
        
    def change_state(self, state):
        self.update_parent()

class LinuxDemoComboBoxWidget(ComboBoxWidget):
    _KEY_VALUES = {'Ubuntu':(2,2), 'Fedora':(1,1), 'Gentoo':(3,3)}

