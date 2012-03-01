#
# Rasterlang (c) Barry Rowlingson 2008
#
#    This file is part of "rasterlang"
#
#    Rasterlang is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Rasterlang is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Rasterlang.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import resources
import layers
import rasters
import os.path

import showform

class MainPlugin(object):
  def __init__(self, iface):
    # Save a reference to the QGIS iface
    self.iface = iface
    self.rd = showform.RasterDialog()
    self.wd = os.path.realpath(os.path.curdir)

  def initGui(self):
    # Create action
    self.action = QAction(QIcon(":/graphics/rastericon.xpm"),"RasterLang",self.iface.mainWindow())
    self.action.setWhatsThis("Raster Manipulation")
    QObject.connect(self.action,SIGNAL("triggered()"),self.run)
    self.iface.addToolBarIcon(self.action)
    self.iface.addPluginToMenu("&RasterLang",self.action)

  def unload(self):
    # Remove the plugin
    self.iface.removePluginMenu("&RasterLang",self.action)
    self.iface.removeToolBarIcon(self.action)

  def run(self):
    self.rd.show()
    self.rd.exec_()

      
