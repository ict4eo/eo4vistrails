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

import ConfigParser
import os.path
p = ConfigParser.ConfigParser()
here = os.path.join(os.path.dirname(__file__),"config.ini")
p.read(here)

def name():
  return p.get('general','name')

def description():
  return p.get('general','description')

def version():
  return p.get('general','version')

def qgisMinimumVersion():
  return p.get("general","qgisMinimumVersion")


def classFactory(iface):
  from main import MainPlugin
  return MainPlugin(iface)

