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
"""
This module provides an generic OGC Simple Features data model via OGR.
All eo4vistrails modules dealing with feature data must extend one of the
provided classes.
"""
# library
import os
import os.path
import urllib
import hashlib
# third-party
import gui.application
try:
    from osgeo import ogr
except:
    import ogr
# vistrails
import core.modules.module_registry
import core.system
from core.modules.vistrails_module import Module, ModuleError
from core.modules.basic_modules import File
# eo4vistrails


class _OgrMemModel():
    """
    Used as both a storage mechanism for MemFeatureModel instances
    and as a general OGR constructor, i.e. whether you want an
    in-memory OGR data provider or not, data will always be passed
    into OGR control via instances of _OgrMemModel
    """

    def __init__(self):
        self.driver = ogr.GetDriverByName('Memory')
        self.datasource = self.driver.CreateDataSource("working_ds")

    def loadContentFromFile(self, sourceDS, getStatement=""):
        """Loads content off filesystem, e.g. from a shapefile

        Expects datasets with one layer, so some arcane formats are out.

        :param str sourceDS:
            a path to a file; allowable file types are:
                {
                shapefiles;
                csv files;
                gml files;
                }
        :param str getStatement:
            a Select statement

        """
        if os.path.exists(sourceDS):
            conn = ogr.Open(sourceDS)
            lyr = conn.GetLayer(0)
            self.datasource.CopyLayer(lyr, lyr.GetName())

            try:
                self.datasource.ReleaseResultLayer(lyr)
            except:
                return
            conn.ReleaseResultSet(lyr)
            conn = None
        else:
            raise ValueError("Path to OGR dataset does not exist")

    def loadContentFromDB(self, connstr, getStatement):
        """Loads content off PostGIS or SpatialLite database.

        :param str connstr:
                connection string
        :param str getStatement:
                a Select statement which defines a layer
        """
        conn = ogr.Open(connstr)
        lyr = conn.ExecuteSQL(getStatement)
        self.datasource.CopyLayer(lyr, lyr.GetName())
        try:
            self.datasource.ReleaseResultLayer(lyr)
        except:
            return
        conn.ReleaseResultSet(lyr)
        conn = None

    def loadContentFromURI(self, webrequest):
        """Loads content off web service, feed etc, e.g. a WFS, GeoRSS

        If an OGR WFS driver was used here, the incoming url might not be
        properly setup.  Also, OGR WFS support requires compiling GDAL/OGR
        with libcurl support.

        This method will implement things a bit more generically.
        The OGR in-memory model will still be used, but not fed by OGR internals.
        Rather, it reads in from a temporary file (e.g. a GML file) retrieved
        by urllib or stream data from urllib into the memory model.

        :param WebRequest webrequest:
            a WebRequest Object, which has `url` and `data` attributes.
            These two variables allow creation of get/post requests, and
            allow OGR to sensibly deal with the inputs.
        """

        #to test, just split, but should use elementtree
        #print getStatement
        fmt = ""
        if webrequest.data:
            test = {
                'responseformat': ('<responseformat>', '</responseformat>'),
                'outputformat': ('outputformat="', '"')}
            getStatement = webrequest.data
            for ky in test:
                try:
                    fmt = getStatement.lower().split(test[ky][0])[1].split(test[ky][1])[0]
                    if fmt:
                        #print fmt
                        break
                except:
                    pass
        else:
            getStatement = ""

        #type = getStatement.lower().split('<responseformat>')
        #type = type[1].split('<responseformat>')[0]

        def _guessOutputType(type_string=""):
            """TO DO Add docstring"""
            if type_string.split(';')[0].lower() == "text/xml":
                #is gml, O&M etc
                return ".xml"
            if type_string.split(';')[0].lower() == "gml2":
                return ".gml"
            else:
                return ".gml"

        def _viaCache():
            """TO DO Add docstring"""
            temp_filepath = core.system.default_dot_vistrails() + "/eo4vistrails/ogr/"
            if not os.path.exists(temp_filepath):
                os.mkdirs(temp_filepath)
            temp_filename = temp_filepath + hashlib.sha1(urllib.quote_plus(webrequest.url + getStatement)).hexdigest() + outputtype
            #core.system.touch(temp_filename)
            postdata = urllib.urlencode({'request': getStatement})
            #print postdata
            u = urllib.urlretrieve(url=webrequest.url, filename=temp_filename, data=postdata,)
            self.loadContentFromFile(temp_filename)

        def _viaStream():
            """TO DO Add docstring"""
            pass

        outputtype = _guessOutputType(fmt)
        #implement first a non-streaming version of this method,
        #i.e. fetches from uri, caches, reads from cache
        _viaCache()

    def loadContentFromString(self, geo_string):
        """Loads up a string of spatial data of some type, e.g. GeoJSON, GML.

        :param str geo_string: a GeoString object such as GMLString, GeoJSONString.
        """

        #TODO FIXME: get rid of string truncation by getting conf from the proper widget
        #- for now, make sure strings are small...

        # Write string to temp file, then load it up
        def _viaCache():
            temp_filepath = core.system.default_dot_vistrails() + "/eo4vistrails/ogr/"

            if not os.path.exists(temp_filepath):
                os.mkdirs(temp_filepath)

            t = str(type(geo_string))
            tl = t.split("'")
            tll = tl[1].split(".")
            gstrtype = tll[len(tll) - 1]

            def _get_ext():
                if gstrtype == "GeoJSONString":
                    return "json"
                if gstrtype == "GMLString":
                    return "gml"

            temp_filename = temp_filepath + hashlib.sha1(
                str(len(geo_string.__dict__['outputPorts']["value_as_string"]))).hexdigest() + "." + _get_ext()  # geo_string.__name__
            f = open(temp_filename, 'w')
            f.write(geo_string.__dict__['outputPorts']["value_as_string"])
            f.close()
            self.loadContentFromFile(temp_filename)
            #os.remove(temp_filename)

        if geo_string != "":
            _viaCache()

    def dumpToFile(self, filesource, datasetType="ESRI Shapefile"):
        """TODO add docstring"""
        # Always overwrites
        if not os.path.exists(filesource):
            os.remove(filesource)  # but for shapefiles? maybe the dataset creation process has an override option rather...

        try:
            driver = ogr.GetDriverByName(datasetType)
            if datasetType == "CSV":
                ds = driver.CreateDataSource(filesource, options=["GEOMETRY=AS_XY"])
                ds.CopyLayer(self.datasource.GetLayer(0), self.datasource.GetLayer(0).GetName(), options=["GEOMETRY=AS_XY"])
            else:
                ds = driver.CreateDataSource(filesource)
                ds.CopyLayer(self.datasource.GetLayer(0), self.datasource.GetLayer(0).GetName())
            filename = ds.GetName()
            ds = None
        except:
            return (False, "")
        return (True, filename)

    def __del__(self):
        """connection resetting, memory deallocation"""
        try:
            self.datasource.ReleaseResultLayer(0)
        except:
            pass
        try:
            self.datasource = None
        except:
            pass


class MemFeatureModel(Module):
    """Retains a copy of an OGR dataset in memory."""

    def __init__(self):
        Module.__init__(self)
        self.feature_model = _OgrMemModel()

    def loadContentFromDB(self, dbconnstr, sql):
        self.feature_model.loadContentFromDB(dbconnstr, sql)

    def loadContentFromFile(self, source_file):
        self.feature_model.loadContentFromFile(source_file)

    def loadContentFromURI(self, webrequest):
        self.feature_model.loadContentFromURI(webrequest)

    def loadContentFromString(self, geo_string):
        self.feature_model.loadContentFromString(geo_string)
#    def dumpToFile(self):
#        print "dumping featuremodel"
#        print self.feature_model

    def compute(self):
        #TODO: make input a file module
        #TODO add string port
        if (self.hasInputFromPort("source_file") and self.getInputFromPort("source_file")):
            source_file = self.getInputFromPort("source_file")
            #self.feature_model.loadContentFromFile(source_file)
            self.loadContentFromFile(source_file)
        elif (self.hasInputFromPort("dbconn") and self.getInputFromPort("dbconn")) \
            and (self.hasInputFromPort("sql") and self.getInputFromPort("sql")):
            #dbconn = self.getInputFromPort("dbconn")
            #sql = self.getInputFromPort("sql")
            #self.feature_model.loadContentFromDB("some connstr", "some SQL")#get sql to execute
            self.loadContentFromDB(self.getInputFromPort("dbconn"), self.getInputFromPort("sql"))
            #self.dumpToFile()
#        elif (self.hasInputFromPort("uri") and self.getInputFromPort("uri")) \
#            and (self.hasInputFromPort("uri_data") and self.getInputFromPort("uri_data")):
#                self.loadContentFromURI(self.getInputFromPort("uri"), self.getInputFromPort("uri_data"))
        elif (self.hasInputFromPort("webrequest") and self.getInputFromPort("webrequest")):
                self.loadContentFromURI(self.getInputFromPort("webrequest"))

        elif (self.hasInputFromPort("gstring") and self.getInputFromPort("gstring")):
                self.loadContentFromString(self.inputPorts["gstring"][0].obj)
        else:
            raise ModuleError(self, 'No source file is supplied - an OGR dataset cannot be generated')

        #self.setResult("feature_dataset", self.feature_model)
        self.setResult("feature_dataset", self)


class FileFeatureModel(File):
    """
    Persists a FeatureModel to disk at a user specified location.

    Likely outputs via OGR would be:
    {shapefile, a postgis database dump, a CSV file ,a GML file, a KML file or GeoJSON}
    """

    def __init__(self):
        File.__init__(self)

    @staticmethod
    def translate_to_python(x):
        result = File()
        result.name = x
        result.setResult("value", result)
        return result

    def compute(self):
        n = self.get_name()
        #TODO: refactor to point to file port rather than source_file
        if (self.hasInputFromPort("source_file") and self.getInputFromPort("source_file")):
            source_file = self.getInputFromPort("source_file")
            print source_file
            if not os.path.isfile(source_file):
                raise ModuleError(self, 'File "%s" does not exist' % source_file)
            ogr = _OgrMemModel()
            ogr.loadContentFromFile(source_file)

        elif (self.hasInputFromPort("source_feature_dataset")):  # and self.getInputFromPort("source_feature_dataset")):
            ogr = self.getInputFromPort("source_feature_dataset").feature_model  # which is the same, an instance of _OgrMemModel
            print ogr
        elif (self.hasInputFromPort("webrequest") and self.getInputFromPort("webrequest")):
            ogr = _OgrMemModel()
            ogr.loadContentFromURI(self.getInputFromPort("webrequest"))
        else:
            raise ModuleError(self, 'No feature_dataset or source file is supplied - an OGR dataset cannot be generated')

        if (self.hasInputFromPort("output_type") and self.getInputFromPort("output_type")):
            output_type = self._ogr_format_check(self.getInputFromPort("output_type"))
        else:
            output_type = "ESRI Shapefile"

        if (self.hasInputFromPort("create_file") and
            self.getInputFromPort("create_file")):
            #core.system.touch(n)
            success, fn = ogr.dumpToFile(n, output_type)
            if success == True:
                #TODO: check if local_filename is necessary?
                self.setResult("local_filename", fn)
                self.setResult("self", self)
                self.set_results(fn)
            else:
                raise ModuleError(self, 'File "%s" does not exist or could not be created' % fn)
        #if not os.path.isfile(n):
        #    raise ModuleError(self, 'File "%s" does not exist' % n)
        #self.set_results(n)
        #self.setResult("local_filename", n)
        #self.setResult("self", self)

    @staticmethod
    def get_widget_class():
        return FileChooserWidget

    def _ogr_format_check(self, fmt):
        supported_ogr_formats = ("ESRI Shapefile", "CSV", "GML", "GeoJSON", "PGDump", "KML")
        fmt = fmt.lstrip()
        fmt = fmt.rstrip()
        fmt = fmt.lower()
        for sfmt in supported_ogr_formats:
            if sfmt.lower() == fmt:
                return sfmt
        return "ESRI Shapefile"


class FeatureModel(Module):
    """This is a common representation of Vector/Feature
    data, sourced from numerous places {postgis, shapefiles, wfs's, gml, etc.}
    Representation is provided by the GDAL/OGR (OGR) library.

    Classes that implement this module are expected to generate the
    internal OGR objects. Optionally, they may expose ports that
    serialise the OGR objects, but that is more likely to take place
    via external serialisers.

    TODO
    .. Should there be an in-memory and a cacheable version of this?
    .. I have had to make SOS NotCacheable to work (Derek, 2010/12/04)
    """

    def __init__(self):
        Module.__init__(self)

    def compute(self):
        """Overriden by subclasses - typically where the
        conversion to an OGR Dataset takes place"""
        pass


class FeatureModelGeometryComparitor(Module):
    """
    Performs geometry comparisons between OGR Geoms.

    Assumes same projection. Is only a double input comparison
    i.e. geomA | geomB. Supports the following comparisons:

    * geomA | geomB : individual geometries compared -> geomB | None
    * geomA | geomSetB : individual geometry compared to a set of geometries -> [geomB's] | None
    * geomSetA | geomB : set of geometries compared to individual geometry -> [geomA's] | None
    * geomSetA | geomSetB : set of geometries compared to a set of geometries -> [(geomA, geomB)] | None

    Operators supported:

    * Predicates: Contains, Crosses, Disjoint, Equal, Intersect, Overlaps, Touches, Within

    For other purposes later:

    * Constructors: Buffer, Centroid, Clone, ConvexHull, Difference, Intersection,
        SymmetricDifference, Union
    * Editors: AddPoint, AddPoint_2D, CloseRings, FlattenTo2D, GetPoint, GetPoint_2D,
        Segmentize, SetCoordinateDimension, SetPoint, SetPoint_2D, Transform,
        TransformTo
    * Calcs: Distance, GetArea, GetBoundary, GetEnvelope,
    * Info: GetCoordinateDimension , GetDimension, GetGeometryCount, GetGeometryName,
        GetGeometryRef, GetGeometryType, GetPointCount, GetSpatialReference,GetX,
        GetY, GetZ IsEmpty, IsRing, IsSimple, IsValid
    """

    def __init__(self):
        Module.__init__()

    def compute(self):
        if (self.hasInputFromPort("geometryA") and self.getInputFromPort("geometryA")):
            geomA = self.getInputFromPort("geometryA")

        if (self.hasInputFromPort("geometrySetA") and self.getInputFromPort("geometrySetA")):
            geomSetA = self.getInputFromPort("geometrySetA")

        if (self.hasInputFromPort("geometryB") and self.getInputFromPort("geometryB")):
            geomA = self.getInputFromPort("geometryB")

        if (self.hasInputFromPort("geometrySetB") and self.getInputFromPort("geometrySetB")):
            geomSetA = self.getInputFromPort("geometrySetB")


def initialize(*args, **keywords):
    """Add module to the Vistrails registry; specify input & output ports."""
    # First create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()
    reg.add_module(FeatureModel)
    #input ports

    #output ports
    reg.add_output_port(
        FeatureModel,
        "OGRDataset",
        (ogr.Dataset, 'Feature data in OGR Dataset'))
