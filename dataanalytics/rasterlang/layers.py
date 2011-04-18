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

try:
    from qgis.core import *
except:
    print "couldnt import qgis, testing mode"
# Get layers: layermap = QgsMapLayerRegistry.instance().mapLayers()

import gdal

class Group:
    def __init__(self,layer,label):
        self.layers=[layer]
        self.labels=[label]
        e = Extent(layer)
        self.info = "Group: %sx%s (%s,%s)-(%s,%s)" % (layer.width(),layer.height(),e.xMinimum(),e.yMinimum(),e.xMaximum(),e.yMaximum())
    def addLayer(self,layer,label):
        self.layers.append(layer)
        self.labels.append(label)

class GroupedLayers:
    def __init__(self):
        self.groups = []
        return
    def addLayer(self,layer,label):
        for group in self.groups:
            if isCompatible(layer,group.layers[0]):
                group.addLayer(layer,label)
                return
        ng = Group(layer,label)
        self.groups.append(ng)
        return
    def findGroup(self,layer):
        groupIndex=0
        for group in self.groups:
            for l in group.layers:
                if l == layer:
                    return groupIndex
            groupIndex=groupIndex+1
        return None


def isCompatible(layer1,layer2):

    # check columns:

    if layer1.width() != layer2.width():
        return False
    if layer1.height() != layer2.height():
        return False

    # compute cell widths
    e1=Extent(layer1)
    w1=e1.width() / layer1.width()
    h1=e1.height() / layer1.height()
    
    e2=Extent(layer2)
    w2=e2.width() / layer2.width()
    h2=e2.height() / layer2.height()

    w=min(w1,w2)
    h=min(h1,h2)
    
    if abs(e1.xMaximum()-e2.xMaximum()) > w:
        return False
    if abs(e1.xMinimum()-e2.xMinimum()) > w:
        return False
    if abs(e1.yMaximum()-e2.yMaximum()) > h:
        return False
    if abs(e1.yMinimum()-e2.yMinimum()) > h:
        return False

    return True

def uniqueLabels(names):
    """ returns a list of unique, valid labels for a list of layer names.
    Where "valid" means conforming to the syntax for rasters in the language."""
    i=1
    labels = []
    from lispy import rasterSyntax
    from pyparsing import LineStart, LineEnd
    validRaster = LineStart() + rasterSyntax() + LineEnd()
    for name in names:
        name1 = name
        try:
            validRaster.parseString(name1)
        except:
            name1 = "layer"
        name2 = name1
        while name1 in labels:
            name1 = name2 + "-%s" % i
            i=i+1
        labels.append(name1)
    return labels
            
            
def layerAsArray(layer):
    """ read the data from a single-band layer into a numpy/Numeric array.
    Only works for gdal layers!
    """
    
    gd = gdal.Open(str(layer.source()))
    array = gd.ReadAsArray()
    return array

def writeGeoTiff(arrayData, extent, path):
    """
    write the given array data to the file 'path' with the given extent.
    
    if arrayData shape is of length 3, then we have multibands (nbad,rows,cols), otherwise one band
    """
    
    format = "GTiff"
    driver = gdal.GetDriverByName( format )
    metadata = driver.GetMetadata()
    if metadata.has_key(gdal.DCAP_CREATE) \
           and metadata[gdal.DCAP_CREATE] == 'YES':
        pass
    else:
        print 'Driver %s does not support Create() method.' % format
        return False

    # get rows and columns
    dims=arrayData.shape
    if len(dims) == 2:
        rows = dims[0]
        cols = dims[1]
        nbands = 1
    else:
        rows = dims[1]
        cols = dims[2]
        nbands = dims[0]

    # could possible use CreateCopy from one of the input rasters...
    
    dst_ds = driver.Create(path, cols, rows, nbands, gdal.GDT_Float32 )

    dst_ds.SetGeoTransform( [
        extent[0] , (extent[2]-extent[0])/cols, 0,
        extent[3], 0, (extent[1]-extent[3])/rows ] )

    if nbands > 1:
        for i in range(nbands):
            dst_ds.GetRasterBand(i+1).WriteArray(arrayData[i])
    else:
        dst_ds.GetRasterBand(1).WriteArray(arrayData)
        
    return True


class Extent:
    def __init__(self,layer):
        """ return an extent-style object with 1.0.0 semantics """
        e = layer.extent()
        try:
            self.xmin = e.xMinimum()
            self.ymin = e.yMinimum()
            self.xmax = e.xMaximum()
            self.ymax = e.yMaximum()
        except:
            self.xmin = e.xMin()
            self.ymin = e.yMin()
            self.xmax = e.xMax()
            self.ymax = e.yMax()
    def xMinimum(self):
        return self.xmin
    def yMinimum(self):
        return self.ymin
    def xMaximum(self):
        return self.xmax
    def yMaximum(self):
        return self.ymax
    def width(self):
        return self.xmax-self.xmin
    def height(self):
        return self.ymax-self.ymin

    
def test():
    layers = QgsMapLayerRegistry.instance().mapLayers().values()
    g = GroupedLayers()
    for l in layers:
        g.addLayer(l,'foo')
    print g
    return g
    

    
def mainTest():
    print uniqueLabels(["Foo","Bar","Baz"])
    print uniqueLabels(["Foo","Foo","Foo","Bar","Bar","Baz"])
    print uniqueLabels(["layer-1","layer-1","layer-1","layer-1-1"])
    print uniqueLabels(["Foo]","B*r","B*r","B() z"])

if __name__=="__main__":
    mainTest()
