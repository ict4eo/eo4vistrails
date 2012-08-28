# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'netcdf4.ui'
#
# Created: Mon Mar  5 15:12:45 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_netcdf4Form(object):
    def setupUi(self, netcdf4Form):
        netcdf4Form.setObjectName(_fromUtf8("netcdf4Form"))
        netcdf4Form.resize(800, 638)
        self.centralwidget = QtGui.QWidget(netcdf4Form)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 0, 781, 541))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.label = QtGui.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(30, 40, 67, 17))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.UrlLineEdit = QtGui.QLineEdit(self.tab)
        self.UrlLineEdit.setGeometry(QtCore.QRect(90, 40, 491, 27))
        self.UrlLineEdit.setObjectName(_fromUtf8("UrlLineEdit"))
        self.fetchVarsButton = QtGui.QPushButton(self.tab)
        self.fetchVarsButton.setGeometry(QtCore.QRect(610, 40, 97, 27))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(75)
        font.setBold(True)
        self.fetchVarsButton.setFont(font)
        self.fetchVarsButton.setObjectName(_fromUtf8("fetchVarsButton"))
        self.treeView = QtGui.QTreeView(self.tab)
        self.treeView.setGeometry(QtCore.QRect(90, 100, 311, 381))
        self.treeView.setAutoExpandDelay(0)
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.groupBox = QtGui.QGroupBox(self.tab)
        self.groupBox.setGeometry(QtCore.QRect(450, 80, 301, 411))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.textMetadata = QtGui.QTextEdit(self.groupBox)
        self.textMetadata.setGeometry(QtCore.QRect(0, 20, 291, 381))
        self.textMetadata.setObjectName(_fromUtf8("textMetadata"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.okButton = QtGui.QPushButton(self.centralwidget)
        self.okButton.setGeometry(QtCore.QRect(560, 560, 97, 27))
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.cancelButton = QtGui.QPushButton(self.centralwidget)
        self.cancelButton.setGeometry(QtCore.QRect(690, 560, 97, 27))
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        #netcdf4Form.setCentralWidget(self.centralwidget)
        #self.menubar = QtGui.QMenuBar(netcdf4Form)
        #self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        #self.menubar.setObjectName(_fromUtf8("menubar"))
        #netcdf4Form.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(netcdf4Form)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        #netcdf4Form.setStatusBar(self.statusbar)

        self.retranslateUi(netcdf4Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(netcdf4Form)

    def retranslateUi(self, netcdf4Form):
        netcdf4Form.setWindowTitle(QtGui.QApplication.translate("netcdf4Form", "netcdf4 Client", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("netcdf4Form", "URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.UrlLineEdit.setText(QtGui.QApplication.translate("netcdf4Form", "/home/mmtsetfwa/Downloads/SSAfrica_MODIS_sst_20110101.nc4", None, QtGui.QApplication.UnicodeUTF8))
        self.fetchVarsButton.setText(QtGui.QApplication.translate("netcdf4Form", "Fetch", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("netcdf4Form", "Metadata", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("netcdf4Form", "NetCDF4 File Variables", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("netcdf4Form", "GetData", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("netcdf4Form", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setShortcut(QtGui.QApplication.translate("netcdf4Form", "C", None, QtGui.QApplication.UnicodeUTF8))
