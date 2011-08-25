#!/usr/bin/env python

import sys
from PyQt4 import Qt
import QTermWidget

a = Qt.QApplication(sys.argv)
w = QTermWidget.QTermWidget(0)
w.setShellProgram('/usr/bin/vim')
w.startShellProgram()
#w.setTerminalFont(Qt.QFont('Terminus'))

w.show()
a.exec_()
