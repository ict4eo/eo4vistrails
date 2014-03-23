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
"""This module provides spatial and temporal selection widgets for configuring
geoinf modules.
"""

from PyQt4 import QtCore, QtGui
from gui.modules.module_configure import StandardModuleConfigurationWidget
from core.modules.module_registry import get_module_registry
from core.modules.vistrails_module import ModuleError
from core.utils import PortAlreadyExists
from core.utils import VistrailsInternalError


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


class SpatioTemporalConfigurationWidgetTabs(QtGui.QTabWidget):
    """Geoinf Configuration Tab Widgets
    are added via the addTab method of the QTabWidget

    """
    def __init__(self, parent=None):
        QtGui.QTabWidget.__init__(self, parent)
        self.setGeometry(QtCore.QRect(20, 20, 790, 540))  # 20, 20, 990, 740
        self.setTabShape(QtGui.QTabWidget.Rounded)
        self.setElideMode(QtCore.Qt.ElideNone)
        self.setObjectName("SpatioTemporalConfigurationWidgetTabsInstance")


class SpatialWidget(QtGui.QWidget):
    """Gather coordinates of a bounding box or, in the case of GRASS, a location

    """

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("SpatialWidget")

        # set holding boxes
        self.metaLayout = QtGui.QHBoxLayout()
        self.gridLayout = QtGui.QGridLayout()
        self.bbox = QtGui.QGroupBox("Bounding Box")
        self.bbox.setLayout(self.gridLayout)
        self.metaLayout.addWidget(self.bbox)
        self.verticalBox = QtGui.QVBoxLayout()
        self.verticalBox.addLayout(self.metaLayout)
        self.verticalBox.insertStretch(-1, 1)  # negative index => space at end
        # overall layout
        self.setLayout(self.verticalBox)
        # add widgets
        self.gridLayout.addWidget(QtGui.QLabel('Top Left X'), 0, 0)
        self.bbox_tlx = QtGui.QLineEdit('-75.102613')
        self.gridLayout.addWidget(self.bbox_tlx, 0, 1)
        self.gridLayout.addWidget(QtGui.QLabel('Top Left Y'), 0, 2)
        self.bbox_tly = QtGui.QLineEdit('40.212597')
        self.gridLayout.addWidget(self.bbox_tly, 0, 3)
        self.gridLayout.addWidget(QtGui.QLabel('Bottom Right X'), 1, 0)
        self.bbox_brx = QtGui.QLineEdit('-72.361859')
        self.gridLayout.addWidget(self.bbox_brx, 1, 1)
        self.gridLayout.addWidget(QtGui.QLabel('Bottom Right Y'), 1, 2)
        self.bbox_bry = QtGui.QLineEdit('41.512517')
        self.gridLayout.addWidget(self.bbox_bry, 1, 3)

    def checkCoords(self, layer_box):
        """Return a warning if layer_box co-ords outside of bounding box co-ords.
        layer_box: tuple (top-left X, top-left Y, bottom-right X, bottom-right Y)

        Using Point in Polygon method

        """
        message = None
        warning = "Warning: POINT (%s) OUT OF BOUNDS... Selected area may be empty!!"
        # setup
        minX = str(layer_box[0])
        minY = str(layer_box[1])
        maxX = str(layer_box[2])
        maxY = str(layer_box[3])
        x1 = str(self.bbox_tlx.text())
        y1 = str(self.bbox_tly.text())
        x2 = str(self.bbox_brx.text())
        y2 = str(self.bbox_bry.text())
        # check
        if minX < x1 < maxX and minY < y1 < maxY:
            pass
        else:
            message = warning % 'X1,Y1'
        if minX < x2 < maxX and minY < y2 < maxY:
            pass
        else:
            message = warning % 'X2,Y2'
        return message

    def getBoundingBox(self):
        """Return a tuple containing box co-ordinates.
        Format: top-left X, top-left Y, bottom-left X, bottom-left Y

        """
        return (
            self.bbox_tlx.text(),
            self.bbox_tly.text(),
            self.bbox_brx.text(),
            self.bbox_bry.text())


class TemporalWidget(QtGui.QWidget):
    """Set temporal bounds and interval parameters for querying datasets
    """

    #TO DO:
    #    use "onChange" methods to call a validation method -
    #    check that the start date is not later than the end date

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("TemporalWidget")
        self.create_temp_config_window()

    def create_temp_config_window(self):
        """TO DO: add docstring"""
        # adding labels and their positions to the main window
        # add and set groupboxes
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.tFramesGroupBox = QtGui.QGroupBox("Time frames")
        self.tFramesLayout = QtGui.QVBoxLayout()

        self.tFramesLayout = QtGui.QGridLayout()
        self.tIntervalLayout = QtGui.QGridLayout()

        self.tFramesGroupBox.setLayout(self.tFramesLayout)
        self.mainLayout.addWidget(self.tFramesGroupBox)

        self.split = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.mainLayout.addWidget(self.split)
        self.intervalsGroupBox = QtGui.QGroupBox("Time interval")
        self.mainLayout.addWidget(self.intervalsGroupBox)
        self.intervalsGroupBox.setLayout(self.tIntervalLayout)
        self.tFramesGroupBox.setLayout(self.tFramesLayout)
        #self.setLayout(self.gridLayout)
        self.tFramesLayout.addWidget(QtGui.QLabel('Start date'), 0, 0)
        self.tFramesLayout.addWidget(QtGui.QLabel('End date'), 1, 0)

        current_date_time = QtCore.QDateTime.currentDateTime()
        current_date = QtCore.QDate.currentDate()
        #setting the start date-time widget and addding it to the window
        self.myTimeStart = QtGui.QDateTimeEdit(current_date_time.addDays(-365))
        #print "STC:170 (create_temp_config_window) MyTimeStr", self.myTimeStart.text()
        self.tFramesLayout.addWidget(self.myTimeStart, 0, 1)
        self.cal1 = QtGui.QCalendarWidget()
        self.cal1.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.cal1.setSelectedDate(current_date.addDays(-365))
        self.myTimeStart.setCalendarPopup(True)
        self.myTimeStart.setCalendarWidget(self.cal1)

        #setting the end date-time widget and addding it to the window
        self.myTimeEnd = QtGui.QDateTimeEdit(current_date_time)
        #print "STC:180 (create_temp_config_window) MyTimeEnd", self.myTimeEnd.text()
        self.tFramesLayout.addWidget(self.myTimeEnd, 1, 1)
        self.cal2 = QtGui.QCalendarWidget()
        self.cal2.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.cal2.setSelectedDate(current_date)
        self.myTimeEnd.setCalendarPopup(True)
        self.myTimeEnd.setCalendarWidget(self.cal2)

        """Code that enables the Slider widget on out temporal tab. this enables
        the user to set the interval for required data """
        """TO DO:
        when ready for execution the signal for the lcd should be
        connected to another external slot to retrieve the lcd value"""
        # DAYS
        # setting up the lcd and the slider widgets
        self.dayLcd = QtGui.QLCDNumber(self)
        self.daySlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        #set layout of Days Slider widget to the grid layout used above
        self.tIntervalLayout.addWidget(QtGui.QLabel('Days'), 3, 0)
        self.tIntervalLayout.addWidget(self.daySlider, 3, 1)
        self.tIntervalLayout.addWidget(self.dayLcd, 3, 2)
        #LCD related
        self.dayLcd.setDigitCount(3)
        #Slider related
        self.daySlider.setRange(0, 364)
        #connecting the signal and slot of the slider and lcd
        self.connect(
            self.daySlider,
            QtCore.SIGNAL('valueChanged(int)'),
            self.dayLcd,
            QtCore.SLOT('display(int)'))
        # HOURS
        # setting up the lcd and the slider widgets
        self.hourLcd = QtGui.QLCDNumber(self)
        self.hourSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        # set layout of Days Slider widget to the grid layout used above
        self.tIntervalLayout.addWidget(QtGui.QLabel('Hours'), 4, 0)
        self.tIntervalLayout.addWidget(self.hourSlider, 4, 1)
        self.tIntervalLayout.addWidget(self.hourLcd, 4, 2)
        # LCD related
        self.hourLcd.setDigitCount(2)
        # Slider related
        self.hourSlider.setRange(0, 23)
        # connecting the signal and slot of the slider and lcd
        self.connect(
            self.hourSlider,
            QtCore.SIGNAL('valueChanged(int)'),
            self.hourLcd,
            QtCore.SLOT('display(int)'))
        # MINUTES
        # setting up the lcd and the slider widgets
        self.minuteLcd = QtGui.QLCDNumber(self)
        self.minuteSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        # set layout of Days Slider widget to the grid layout used above
        self.tIntervalLayout.addWidget(QtGui.QLabel('Minutes'), 5, 0)
        self.tIntervalLayout.addWidget(self.minuteSlider, 5, 1)
        self.tIntervalLayout.addWidget(self.minuteLcd, 5, 2)
        # LCD related
        self.minuteLcd.setDigitCount(2)
        # Slider related
        self.minuteSlider.setRange(0, 59)
        # connecting the signal and slot of the slider and lcd
        self.connect(
            self.minuteSlider,
            QtCore.SIGNAL('valueChanged(int)'),
            self.minuteLcd,
            QtCore.SLOT('display(int)'))

    def getTimeBegin(self):
        """Return a string with begin time in UTC format."""
        _time = self.myTimeStart.toString(DATETIME_FORMAT)
        #print "STC:251 gettimeStart", type(_time), _time
        return _time
        #py_time = _time.toPyDateTime()  # same as Python date/time
        #return py_time.strftime(DATETIME_FORMAT)

    def getTimeEnd(self):
        """Return a string with end time in UTC format."""
        """Return a string with begin time in UTC format."""
        _time = self.myTimeEnd.toString(DATETIME_FORMAT)
        #print "STC:260 gettimeEnd", type(_time), _time
        return _time
        """
        _time = self.myTimeEnd.dateTime()
        py_time = _time.toPyDateTime()  # same as Python date/time
        return py_time.strftime(DATETIME_FORMAT)
        """

    def getTimeInterval(self):
        """Return a tuple containing begin / end time strings in UTC format."""
        return (
            self.getTimeBegin(),
            self.getTimeEnd())

    def setTimeInterval(self, begin=None, end=None):
        """Set the time values for the widgets based on date/time objects.

        Also try using string->date conversion
        """
        #print "STC:280 begin end", type(begin), begin, end
        try:
            if begin:
                self.myTimeStart = QtGui.QDateTimeEdit(begin)
            if end:
                self.myTimeEnd = QtGui.QDateTimeEdit(end)
        except:
            #try:
            # try to convert strings into dates
            if begin:
                self.myTimeStart = QtCore.QDateTime.fromString(
                    begin, DATETIME_FORMAT)
            if end:
                self.myTimeEnd = QtCore.QDateTime.fromString(
                    end, DATETIME_FORMAT)
            #except:
            #    pass
        #print "STC:297 ", type(self.myTimeStart)
        #print "STC:298 (set time interval) MyTimeS", self.myTimeStart.toString(QtCore.Qt.ISODate)
        #print "STC:299 (set time interval) MyTimeE", self.myTimeEnd.toString(QtCore.Qt.ISODate)

    def resetTime(self):
        """Set the default time values for the widgets."""
        current_date_time = QtCore.QDateTime.currentDateTime()
        self.myTimeStart = QtGui.QDateTimeEdit(current_date_time.addDays(-365))
        self.myTimeEnd = QtGui.QDateTimeEdit(current_date_time)
        #print "STC:306 (reset time) MyTimeS", self.myTimeStart.toString(QtCore.Qt.ISODate)
        #print "STC:307 (reset time) MyTimeE", self.myTimeEnd.toString(QtCore.Qt.ISODate)


class SpatialTemporalConfigurationWidget(StandardModuleConfigurationWidget):
    """makes use of code style from TupleConfigurationWidget"""
    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, parent)
        #FOO = module.getInputFromPort(OGC_URL_PORT)  # TEST REMOVE !!!!!!!!!!!!
        # initialise the setup necessary for all geoinf widgets that follow
        self.setWindowTitle('Geo Configuration Parameters')
        self.setToolTip("Setup service, spatial and temporal parameters for working with a geoinf module")
        self.createTabs()
        self.createButtons()
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().addLayout(self.tabLayout)
        self.layout().addLayout(self.buttonLayout)
        #self.create_config_window()

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        traceback.print_exc()
        raise ModuleError(self, msg + ': %s' % str(error))

    def updateVistrail(self):
        """TO DO - add docstring"""
        msg = "updateVistrail() is not yet implemented in this subclass"
        raise VistrailsInternalError(msg)

    def createTabs(self):
        """ createTabs() -> None
        create and populate with widgets the necessary
        tabs for spatial and temporal parameterisation

        """
        self.tabs = SpatioTemporalConfigurationWidgetTabs()
        self.spatial_widget = SpatialWidget()
        self.temporal_widget = TemporalWidget()
        self.tabs.addTab(self.spatial_widget, "")
        self.tabs.addTab(self.temporal_widget, "")

        self.tabs.setTabText(
            self.tabs.indexOf(self.spatial_widget),
            QtGui.QApplication.translate(
                "SpatialTemporalConfigurationWidget",
                "Bounding Coordinates",
                None,
                QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.spatial_widget),
            QtGui.QApplication.translate(
                "SpatialTemporalConfigurationWidget",
                "Gather coordinates of a bounding box or, in the case of GRASS, a location",
                None,
                QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabText(
            self.tabs.indexOf(self.temporal_widget),
            QtGui.QApplication.translate(
                "SpatialTemporalConfigurationWidget",
                "Temporal Bounds and Intervals",
                None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.temporal_widget),
            QtGui.QApplication.translate(
                "SpatialTemporalConfigurationWidget",
                "Choose and set temporal bounds and interval parameters",
                None,
                QtGui.QApplication.UnicodeUTF8))
        self.tabLayout = QtGui.QHBoxLayout()
        self.tabLayout.addWidget(self.tabs)
        self.tabs.setCurrentIndex(0)
        self.tabs.setVisible(True)

    def createButtons(self):
        """ createButtons() -> None
        Create and connect signals to Ok & Cancel button

        """
        self.buttonLayout = QtGui.QHBoxLayout()
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

    def sizeHint(self):
        """ sizeHint() -> QSize
        Return the recommended size of the configuration window

        """
        return QtCore.QSize(800, 600)

    def getTimeInterval(self):
        """Return a tuple containing begin / end in universal time.

        """
        return (
            self.temporal_widget.getTimeBegin(),
            self.temporal_widget.getTimeEnd(),)

    def getBoundingBox(self):
        """Return a tuple containing valid box co-ordinates, or None.
        Format: top-left X, top-left Y, bottom-left X, bottom-left Y

        """
        try:
            if float(spatial_widget.bbox_tlx.text()) and \
               float(spatial_widget.bbox_tly.text()) and \
               float(spatial_widget.bbox_brx.text()) and \
               float(spatial_widget.bbox_bry.text()):
                return (
                    self.spatial_widget.bbox_tlx.text(),
                    self.spatial_widget.bbox_tly.text(),
                    self.spatial_widget.bbox_brx.text(),
                    self.spatial_widget.bbox_bry.text())
        except:
            return None

    def getBoundingBoxString(self):
        """Return a comma-delimited string containing valid box co-ordinates,
        or None.

        """
        bbox = self.getBoundingBox()
        if bbox:
            return str(bbox[0]) + ',' + str(bbox[1]) + ',' + \
                   str(bbox[2]) + ',' + str(bbox[3])
        else:
            return None

    def okTriggered(self, checked=False, functions=[]):
        """ okTriggered(checked: bool, functions: array) -> None
        Extend in a subclass to set configuration on the module ports

        """
        #print "OK Triggered in SpatialTemporalConfigurationWidget (line 411)"
        self.close()
