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
"""This module is used to define combobox widgets which can be attached to a
module's port to provide simple (and controlled) selection of pre-defined options.
"""
debug = False

# thirdparty
from PyQt4 import QtCore, QtGui
# vistrails
from core.modules.constant_configuration import ConstantWidgetMixin


class ComboBoxWidget(QtGui.QComboBox, ConstantWidgetMixin):
    """Base class for module port combobox.
    
    Subclass this class to make your own combobox widget with its own list
    by setting the value of _KEY_VALUES or by redefining getKeyValues().
    
    NOTE: Keys *must* be strings in the dict
    """

    _KEY_VALUES = {'please': '1', 'set': '2', 'values': '3'}
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

        if debug: print "1->", param.strValue
        for (k, v) in self.getKeyValues().items():
            if debug: print "2->", k, v
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

        for (k, v) in keyvalues.items():
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


class DateFormatComboBoxWidget(ComboBoxWidget):
    """Marker constants used for date formatting on a matplotlib date plot."""

    _KEY_VALUES = {'YYYY-MM-DD': '%Y-%m-%d',
                   'MM-DD-YYYY': '%m-%d-%Y',
                   'YYYY-MM-DD HH:MM:SS': '%Y-%m-%d %H:%M:%S',
                   'YYYY-MM-DD HH:MM:SSZ': '%Y-%m-%d %H:%M:%SZ',
                   'YYYY-M-MDDTHH:MM:SS.n': '%Y-%m-%dT%H:%M:%S.%f'}


class LinuxDemoComboBoxWidget(ComboBoxWidget):
    """Example for defining port combobox values."""

    _KEY_VALUES = {'Ubuntu': (2, 2), 'Fedora': (1, 1), 'Gentoo': (3, 3),
                   'Mint': (0, 0)}
