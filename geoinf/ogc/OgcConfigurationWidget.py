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
selection widgets for configuring geoinf.ogc modules.

This refers primarily to GetCapabilities requests
"""

from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.SpatialTemporalConfigurationWidget \
    import SpatialTemporalConfigurationWidget
from Common import OgcService  # include owslib .wfs, .sos, .wcs
from core.modules.vistrails_module import ModuleError
import init


class OgcCommonWidget(QtGui.QWidget):
    """TO DO - add docstring"""
    def __init__(self, module, parent=None):
        '''parses modules attributes to fetch parameters'''
        QtGui.QWidget.__init__(self, parent)
        self.launchtype = str(module).split(" ")[1].split(":")[1][0:3].lower()
        #self.module = module
        self.setObjectName("OgcCommonWidget")
        self.parent_widget = module
        self.service = None
        self.create_config_window()

    def create_config_window(self):
        """TO DO - add docstring"""
        self.setWindowTitle("General OGC Configuration Widget")
        self.setMinimumSize(800, 350)
        self.center()
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        if self.launchtype == "sos":
            self.urlGroupBox = QtGui.QGroupBox("OGC Sensor Observation Service:")
            self.line_edit_OGC_url = QtGui.QLineEdit(
                "http://giv-sos.uni-muenster.de:8080/52nSOSv3/sos" #?request=GetCapabilities&service=SOS"
                )
        elif self.launchtype == "wfs":
            self.urlGroupBox = QtGui.QGroupBox("OGC Web Feature Service:")
            self.line_edit_OGC_url = QtGui.QLineEdit(
                'http://ict4eo.meraka.csir.co.za:8080/geoserver/wfs'
                )
        elif self.launchtype == "wcs":
            self.urlGroupBox = QtGui.QGroupBox("OGC Web Coverage Service:")
            self.line_edit_OGC_url = QtGui.QLineEdit('http://afis.meraka.org.za/geoserver/wcs')
        else:
            self.urlGroupBox = QtGui.QGroupBox("OGC Service:")
        self.fetchUrlLayout = QtGui.QHBoxLayout()

        self.label_OGC_url = QtGui.QLabel('URL & Version:')

        self.launchversion = QtGui.QComboBox()
        if self.launchtype == "sos":
            self.launchversion.addItems(['1.0.0',])
        elif self.launchtype == "wfs":
            self.launchversion.addItems(['1.0.0','1.1.0'])
        elif self.launchtype == "wcs":
            self.launchversion.addItems(['1.0.0','1.1.0'])
        else:
            self.launchversion.addItems(['1.0.0',])

        self.fetchButton = QtGui.QPushButton('&Fetch')
        self.fetchButton.setAutoDefault(False)

        self.fetchUrlLayout.addWidget(self.label_OGC_url)
        self.fetchUrlLayout.addWidget(self.line_edit_OGC_url)
        self.fetchUrlLayout.addWidget(self.launchversion)
        self.fetchUrlLayout.addWidget(self.fetchButton)

        self.urlGroupBox.setLayout(self.fetchUrlLayout)

        self.mainLayout.addWidget(self.urlGroupBox)

        self.metaLayout = QtGui.QHBoxLayout()
        self.metaGroupBox = QtGui.QGroupBox("Service Metadata")
        self.metaGroupBox.setLayout(self.metaLayout)
        self.mainLayout.addWidget(self.metaGroupBox)

        self.serviceIDLayout = QtGui.QVBoxLayout()
        self.serviceIDGroupBox = QtGui.QGroupBox("Service Identification")
        self.serviceIDGroupBox.setLayout(self.serviceIDLayout)
        self.serviceIDServiceTable = QtGui.QTableWidget()
        self.serviceIDServiceTable.setRowCount(7)
        self.serviceIDServiceTable.setColumnCount(1)
        ogc_dummy = OgcService('','SOS','1.0.0') #placeholder; use to get row labels

        row_position = 0
        for item in ogc_dummy.service_id_key_set:
            service_id_list_item = item.values()[0]
            qtwi = QtGui.QTableWidgetItem(service_id_list_item) # row label
            self.serviceIDServiceTable.setVerticalHeaderItem(row_position, qtwi)
            row_position = row_position + 1
        self.serviceIDServiceTable.setHorizontalHeaderLabels (['', ])
        self.serviceIDServiceTable.setAutoScroll(True)
        self.serviceIDServiceTable.setWordWrap(True)
        self.serviceIDServiceTable.horizontalHeader().setStretchLastSection(True)
        self.serviceIDLayout.addWidget(self.serviceIDServiceTable)
        self.metaLayout.addWidget(self.serviceIDGroupBox)

        self.servicePublisherLayout = QtGui.QVBoxLayout()
        self.servicePublisherGroupBox = QtGui.QGroupBox("Publisher Details")
        self.servicePublisherGroupBox.setLayout(self.servicePublisherLayout)

        self.servicePublisherTable = QtGui.QTableWidget()
        self.servicePublisherTable.setRowCount(17)
        self.servicePublisherTable.setColumnCount(1)

        row_position = 0
        for item in ogc_dummy.provider_key_set:
            provider_id_list_item = item.values()[0]
            qtwi = QtGui.QTableWidgetItem(provider_id_list_item)  # row label
            self.servicePublisherTable.setVerticalHeaderItem(row_position, qtwi)
            row_position = row_position + 1
        self.servicePublisherTable.setHorizontalHeaderLabels (['',])
        self.servicePublisherTable.setAutoScroll(True)
        self.servicePublisherTable.setWordWrap(True)
        self.servicePublisherTable.horizontalHeader().setStretchLastSection(True)
        self.servicePublisherLayout.addWidget(self.servicePublisherTable)
        self.metaLayout.addWidget(self.servicePublisherGroupBox)
        # cursors
        self.waitCursor = QtGui.QCursor(QtCore.Qt.WaitCursor)
        self.arrowCursor = QtGui.QCursor(QtCore.Qt.ArrowCursor)
        # signals
        self.connect(
            self.fetchButton,
            QtCore.SIGNAL('clicked(bool)'),
            self.fetchTriggered
            )

    def center(self):
        """TO DO - add docstring"""
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def fetchTriggered(self):
        """TO DO - add docstring"""
        if self.line_edit_OGC_url.text() != "":
            #print "lvct" + str(self.launchversion.currentText())
            self.setCursor(self.waitCursor)
            self.serviceIDServiceTable.clearContents()
            self.servicePublisherTable.clearContents()

            self.service = OgcService(
                self.line_edit_OGC_url.text(),
                self.launchtype,
                str(self.launchversion.currentText())
                )
            self.setCursor(self.arrowCursor)
            # populate metadata
            if self.service.service_valid:
                # service id metadata
                row_count = 0
                for item in self.service.service_id_key_set:
                    service_id_dict_item = item.keys()[0]
                    if self.service.__dict__.has_key(service_id_dict_item):
                        qtwi = QtGui.QTableWidgetItem(
                            str(self.service.__dict__[service_id_dict_item])
                            )
                        self.serviceIDServiceTable.setItem (row_count, 0, qtwi)
                    row_count = row_count + 1
                # provider metadata
                # N.B. OGC WFS 1.0.0 does not have provider metadata in this form
                if self.launchtype == "wfs" and self.launchversion.currentText() == "1.0.0":
                    #TODO: we need to indicate visually that no meta data is present
                    pass
                else:
                    row_count = 0
                    for item in self.service.provider_key_set:
                        provider_dict_item = item.keys()[0]
                        if self.service.__dict__.has_key(provider_dict_item):
                           qtwi = QtGui.QTableWidgetItem(
                                str(self.service.__dict__[provider_dict_item])
                                )
                           self.servicePublisherTable.setItem (row_count, 0, qtwi)
                        row_count = row_count + 1
                # fire a "done" event: can be "listened for" in children
                self.emit(QtCore.SIGNAL('serviceActivated'))

            else:
                self.emit(QtCore.SIGNAL('serviceDeactivated'))
                self.showWarning(
                    'Unable to activate service:\n \
Please check configuration & network.\n'\
                    +self.service.service_valid_error
                    )
        else:
            # TODO - should not get here; maybe disable Fetch button until text entered?
            pass

    def showWarning(self, message):
        """Show user a warning dialog."""
        self.setCursor(self.arrowCursor)
        QtGui.QMessageBox.warning(self,"Warning",message,QtGui.QMessageBox.Ok)


class OgcConfigurationWidget(SpatialTemporalConfigurationWidget):
    """TO DO - add docstring"""
    def __init__(self, module, controller, parent=None):
        SpatialTemporalConfigurationWidget.__init__(self, module, controller, parent)
        # will be used by children classes to access signals
        self.ogc_common_widget = OgcCommonWidget(module)
        # set basic configuration tabs
        self.tabs.insertTab(0, self.ogc_common_widget, "")
        self.tabs.setTabText(
            self.tabs.indexOf(self.ogc_common_widget),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "Service Metadata",
                None,
                QtGui.QApplication.UnicodeUTF8
                )
            )
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.ogc_common_widget),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "Inspect basic service metadata for your chosen OGC service",
                None,
                QtGui.QApplication.UnicodeUTF8
                )
            )
        # set other common properties
        self.waitCursor = QtGui.QCursor(QtCore.Qt.WaitCursor)
        self.arrowCursor = QtGui.QCursor(QtCore.Qt.ArrowCursor)

    def showWarning(self, message):
        """Show user a warning dialog."""
        self.setCursor(self.arrowCursor)
        QtGui.QMessageBox.warning(self,'Warning',message,QtGui.QMessageBox.Ok)

    def showError(self, message):
        """Show user an error dialog."""
        self.setCursor(self.arrowCursor)
        QtGui.QMessageBox.critical(self, 'Error',message,QtGui.QMessageBox.Ok)

    def okTriggered(self): # , checked=False in parent?
        """Extends method defined in SpatialTemporalConfigurationWidget."""
        print "=== OK Triggered in OgcConfigurationWidget (line 265) ==="
        full_url = self.ogc_common_widget.line_edit_OGC_url.text()
        if '?' in full_url:
            parts = full_url.split('?')
            self.url = parts[0]
        else:
            self.url = full_url
        result = self.constructRequest()
        self.request_type = result[0] or None
        self.data = result[1] or None
        print "OgcConfigurationWidget.py:276 (url,result,data,type)\n", \
            self.url, result, self.data, self.request_type
        # must not set ports if nothing has been specified, or
        # if there was a problem constructing the request
        if self.data and self.request_type:
            functions = []
            functions.append(
                (init.OGC_URL_PORT,[self.url]),
                )
            if self.request_type == 'GET':
                functions.append(
                    (init.OGC_GET_REQUEST_PORT,[self.data]),
                    )
            elif self.request_type == 'POST':
                functions.append(
                    (init.OGC_POST_REQUEST_PORT,[self.data]),
                    )
            else:
                raise ModuleError(
                    self,
                    'Unknown OgcService request type' + ': %s' % str(self.request_type)
                )
            # see: gui.vistrails_controller.py
            self.controller.update_ports_and_functions(
                self.module.id, [], [], functions
                )
            SpatialTemporalConfigurationWidget.okTriggered(self)
        else:
            pass # TO DO - is this correct?  need to inform user?

    def constructRequest(self):
        """Return a request type (GET/POST) and request from parameters.

        Overwrite in a subclass to set the service specific parameters.
        """
        return None, None
