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
"""This module is used to add threading ability to VisTrails via the RPyC
package.  If this package is not available, "dummy" modules will allow other
code to continue to work.
"""
#QT
from PyQt4 import QtGui, QtCore
# global
import copy
import sys
# vistrails
from core.modules.vistrails_module import Module, NotCacheable, \
        InvalidOutput, ModuleError, ModuleBreakpoint, ModuleErrors
import core.packagemanager
from packages.controlflow.fold import *


class ThreadSafeMixin():
    """Placeholder class; overwritten by module from
    *packages.rpyc4vistrails.ThreadSafe*, if available."""

    def __init__(self):
        pass


class Fork(ThreadSafeMixin, NotCacheable, Module):
    pass


class ThreadSafeFold(ThreadSafeMixin, Fold):
    pass


class ThreadSafeMap(ThreadSafeFold):
    pass


class ThreadTestModule(ThreadSafeMixin, Module):  # NotCacheable,
    pass


# import either actual, or "dummy" rpyc modules
#needs same aggresive approach as seen in RPYC
#manager = core.packagemanager.get_package_manager()
#if manager.has_package('za.co.csir.rpyc4vistrails'):
#    from packages.rpyc4vistrails.ThreadSafe import  \
#        ThreadSafeMixin, ThreadSafeFold, ThreadSafeMap, ThreadTestModule, Fork

try:
    from packages.rpyc4vistrails.ThreadSafe import  \
        ThreadSafeMixin, ThreadSafeFold, ThreadSafeMap, ThreadTestModule, Fork
except ImportError:
    pass
"""
else:
    ThreadSafeMixin = _ThreadSafeMixin
    ThreadSafeFold = _ThreadSafeFold
    ThreadSafeMap = _ThreadSafeMap
    ThreadTestModule = _ThreadTestModule
    Fork = _Fork
"""