###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation
## ingestion, pre-processing, transformation, analytic and visualisation
## capabilities . Included is the abilty to run code transparently in
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
"""This abstract module provides string specialisations that allow modules to
understand what kind of data is being passed into a method as a string.
"""
# library
# third-party
from PyQt4 import QtCore, QtGui
# vistrails
from core.modules import basic_modules
from core.utils import any, expression
from core.modules.constant_configuration import ConstantWidgetMixin
# eo4vistrails


#class GMLString(GeoString):
#    pass
#
#class WKTString(GeoString):
#    pass
#
#class GeoJSONString(GeoString):
#    pass
    #TODO:  this needs to be upgraded to 1.6.1 to take advantage of the ability
    #       to specify the  port which receives the output


class GeoStringConstantWidget(QtGui.QTextEdit, ConstantWidgetMixin):
    """
    GeoString is a basic widget to be used
    to edit gml, geojson, wkt string values in VisTrails.

    When creating your own widget, you can subclass from this widget if you
    need only a QLineEdit or use your own QT widget. There are two things you
    need to pay attention to:

    1) Re-implement the contents() method so we can get the current value
       stored in the widget.

    2) When the user is done with configuration, make sure to call
       update_parent() so VisTrails can pass that information to the Provenance
       System. In this example we do that on focusOutEvent and when the user
       presses the return key.

    """
    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)

        Initialize the line edit with its contents. Content type is limited
        to 'int', 'float', and 'string'

        """
        QtGui.QTextEdit.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        # assert param.namespace == None
        # assert param.identifier == 'edu.utah.sci.vistrails.basic'
        contents = param.strValue
        contentType = param.type
        self.setText(contents)
        self._contentType = contentType
        self.connect(self,
                     QtCore.SIGNAL('returnPressed()'),
                     self.update_parent)

    def contents(self):
        """contents() -> str
        Re-implement this method to make sure that it will return a string
        representation of the value that it will be passed to the module
        As this is a QLineEdit, we just call text()

        """
        self.update_text()
        return str(self.toPlainText())

    def setContents(self, strValue, silent=True):
        """setContents(strValue: str) -> None
        Re-implement this method so the widget can change its value after
        constructed. If silent is False, it will propagate the event back
        to the parent.
        As this is a QLineEdit, we just call setText(strValue)
        """
        self.setText(strValue)
        self.update_text()
        if not silent:
            self.update_parent()

    def update_text(self):
        """ update_text() -> None
        Update the text to the result of the evaluation

        """
        # FIXME: eval should pretty much never be used
        base = expression.evaluate_expressions(self.toPlainText())
        if self._contentType == 'String':
            self.setText(base)
        else:
            try:
                self.setText(str(eval(str(base), None, None)))
            except:
                self.setText(base)

    def sizeHint(self):
        metrics = QtGui.QFontMetrics(self.font())
        width = min(metrics.width(self.toPlainText()) + 10, 70)
        return QtCore.QSize(width,
                            metrics.height() + 60)

    def minimumSizeHint(self):
        return self.sizeHint()

    ###########################################################################
    # event handlers

    def focusInEvent(self, event):
        """ focusInEvent(event: QEvent) -> None
        Pass the event to the parent

        """
        self._contents = str(self.toPlainText())
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        QtGui.QTextEdit.focusInEvent(self, event)

    def focusOutEvent(self, event):
        self.update_parent()
        QtGui.QTextEdit.focusOutEvent(self, event)
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)


GeoString = basic_modules.new_constant('GeoString',
                                        staticmethod(str),
                                        None,
                                        staticmethod(lambda x: type(x) == str),
                                        GeoStringConstantWidget)
GMLString = basic_modules.new_constant('GMLString',
                                        staticmethod(str),
                                        None,
                                        staticmethod(lambda x: type(x) == str),
                                        GeoStringConstantWidget)
WKTString = basic_modules.new_constant('WKTString',
                                        staticmethod(str),
                                        "",
                                        staticmethod(lambda x: type(x) == str),
                                        GeoStringConstantWidget)
GeoJSONString = basic_modules.new_constant('GeoJSONString',
                                        staticmethod(str),
                                        None,
                                        staticmethod(lambda x: type(x) == str),
                                        GeoStringConstantWidget)
Proj4String = basic_modules.new_constant('Proj4String',
                                        staticmethod(str),
                                        None,
                                        staticmethod(lambda x: type(x) == str),
                                        GeoStringConstantWidget)


#class GeoStringConfigurationWidget(SourceConfigurationWidget):
#    """TODO Add doc string"""
#
#    def __init__(self, module, controller, parent=None):
#        SourceConfigurationWidget.__init__(self, module, controller, None,
#                                           False, False, parent)
