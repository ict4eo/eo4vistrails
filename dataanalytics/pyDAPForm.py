# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/mmtsetfwa/Documents/Cluva/pyDAP.ui'
#
# Created: Thu Jan 26 13:18:12 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_pyDAPForm(object):
    def setupUi(self, pyDAPForm):
        pyDAPForm.setObjectName(_fromUtf8("pyDAPForm"))
        pyDAPForm.resize(800, 638)
        self.centralwidget = QtGui.QWidget(pyDAPForm)
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
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.okButton = QtGui.QPushButton(self.centralwidget)
        self.okButton.setGeometry(QtCore.QRect(560, 560, 97, 27))
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.cancelButton = QtGui.QPushButton(self.centralwidget)
        self.cancelButton.setGeometry(QtCore.QRect(690, 560, 97, 27))
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        #pyDAPForm.setCentralWidget(self.centralwidget)
        #self.menubar = QtGui.QMenuBar(pyDAPForm)
        #self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        #self.menubar.setObjectName(_fromUtf8("menubar"))
        #pyDAPForm.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(pyDAPForm)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        #pyDAPForm.setStatusBar(self.statusbar)

        self.retranslateUi(pyDAPForm)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(pyDAPForm)

    def retranslateUi(self, pyDAPForm):
        pyDAPForm.setWindowTitle(QtGui.QApplication.translate("pyDAPForm", "pyDAP Client", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("pyDAPForm", "Url:", None, QtGui.QApplication.UnicodeUTF8))
        self.UrlLineEdit.setText(QtGui.QApplication.translate("pyDAPForm", "http://ict4eo1.dhcp.meraka.csir.co.za/pydap/ccam_atlas_csiro.210012.nc", None, QtGui.QApplication.UnicodeUTF8))
        self.fetchVarsButton.setText(QtGui.QApplication.translate("pyDAPForm", "Fetch", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("pyDAPForm", "Metadata", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("pyDAPForm", "NetCDF File Variables", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("pyDAPForm", "Variable Dimensions", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("pyDAPForm", "GetData", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("pyDAPForm", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setShortcut(QtGui.QApplication.translate("pyDAPForm", "C", None, QtGui.QApplication.UnicodeUTF8))

