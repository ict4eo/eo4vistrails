======
GeoInf
======

.. toctree::
   :maxdepth: 6

.. automodule:: geoinf
   :members:


DataModels
==========

.. automodule:: geoinf.datamodels


DataRequest
-----------

.. automodule:: geoinf.datamodels.DataRequest
   :members:
   :undoc-members:

.. autoclass:: geoinf.datamodels.DataRequest.DataRequest
   :members:
   :undoc-members:


Feature
-------

.. automodule:: geoinf.datamodels.Feature
   :members:
   :undoc-members:

.. autoclass:: FeatureModel
   :members:
   :undoc-members:
.. autoclass:: MemFeatureModel
   :members:
   :undoc-members:
.. autoclass:: FileFeatureModel
   :members:
   :undoc-members:
.. autoclass:: FeatureModelGeometryComparitor
   :members:
   :undoc-members:


QgsLayer
--------

.. automodule:: geoinf.datamodels.QgsLayer
   :members:
   :undoc-members:

.. autoclass:: geoinf.datamodels.QgsLayer.QgsMapLayer
   :members:
   :undoc-members:
.. autoclass:: geoinf.datamodels.QgsLayer.QgsVectorLayer
   :members:
   :undoc-members:
.. autoclass:: geoinf.datamodels.QgsLayer.QgsRasterLayer
   :members:
   :undoc-members:


QgsLayerWriter
--------------

.. automodule:: geoinf.datamodels.QgsLayerWriter
   :members:
   :undoc-members:

.. autoclass:: geoinf.datamodels.QgsLayerWriter.QgsLayerWriter
   :members:
   :undoc-members:


Raster
------

.. automodule:: geoinf.datamodels.Raster
   :members:
   :undoc-members:

.. autoclass:: geoinf.datamodels.Raster._GdalMemModel
   :members:
   :undoc-members:
.. autoclass:: geoinf.datamodels.Raster.RasterModel
   :members:
   :undoc-members:


RasterImport
-------------

.. automodule:: geoinf.datamodels.RasterImport
   :members:
   :undoc-members:

.. autoclass:: geoinf.datamodels.RasterImport.RasterImport
   :members:
   :undoc-members:
.. autoclass:: geoinf.datamodels.RasterImport.RasterImportCommonWidget
   :members:
   :undoc-members:
.. autoclass:: geoinf.datamodels.RasterImport.RasterImportConfigurationWidget
   :members:
   :undoc-members:


TemporalVectorLayer
-------------------

.. automodule:: geoinf.datamodels.TemporalVectorLayer
   :members:
   :undoc-members:

.. autoclass:: geoinf.datamodels.TemporalVectorLayer.TemporalVectorLayer
   :members:
   :undoc-members:


WebRequest
-----------

.. automodule:: geoinf.datamodels.WebRequest
   :members:
   :undoc-members:

.. autoclass:: geoinf.datamodels.WebRequest.WebRequest
   :members:
   :undoc-members:


GeoStrings
==========

.. automodule:: geoinf.geostrings


GeoJSON
-------

.. automodule:: geoinf.geostrings.GeoJSON
   :members:
   :undoc-members:

.. autoclass:: geoinf.geostrings.GeoJSON.GeoJSONModule
   :members:
   :undoc-members:

.. autoclass:: geoinf.geostrings.GeoJSON.GJFeature
   :members:
   :undoc-members:

GeoStrings
----------

.. automodule:: geoinf.geostrings.GeoStrings
   :members:
   :undoc-members:

.. autoclass:: geoinf.geostrings.GeoStrings.GeoStringConstantWidget
   :members:
   :undoc-members:


Helpers
========

.. automodule:: geoinf.helpers


AOI_Utils
---------

.. automodule:: geoinf.helpers.AOI_Utils
   :members:
   :undoc-members:

.. autoclass:: geoinf.helpers.AOI_Utils.SRSChooserDialog
   :members:
   :undoc-members:

.. autoclass:: geoinf.helpers.AOI_Utils.GetFeatureInfoTool
   :members:
   :undoc-members:

.. autoclass:: geoinf.helpers.AOI_Utils.FeatureOfInterestDefiner
   :members:
   :undoc-members:

.. autoclass:: geoinf.helpers.AOI_Utils.AreaOfInterestDefiner
   :members:
   :undoc-members:

.. autoclass:: geoinf.helpers.AOI_Utils.LineOfInterestDefiner
   :members:
   :undoc-members:

.. autoclass:: geoinf.helpers.AOI_Utils.PointOfInterestDefiner
   :members:
   :undoc-members:

.. autoclass:: geoinf.helpers.AOI_Utils.FeatureOfInterestDefinerConfigurationWidget
   :members:
   :undoc-members:


PostGIS
==========

.. automodule:: geoinf.postgis

PostGIS
--------

.. automodule:: geoinf.postgis.PostGIS
   :members:
   :undoc-members:

.. autoclass:: geoinf.postgis.PostGIS.PostGisSession
   :members:
   :undoc-members:

.. autoclass:: geoinf.postgis.PostGIS.PostGisNumpyReturningCursor
   :members:
   :undoc-members:

.. autoclass:: geoinf.postgis.PostGIS.PostGisFeatureReturningCursor
   :members:
   :undoc-members:

.. autoclass:: geoinf.postgis.PostGIS.PostGisBasicReturningCursor
   :members:
   :undoc-members:

.. autoclass:: geoinf.postgis.PostGIS.PostGisNonReturningCursor
   :members:
   :undoc-members:

.. autoclass:: geoinf.postgis.PostGIS.PostGisCopyFrom
   :members:
   :undoc-members:

.. autoclass:: geoinf.postgis.PostGIS.PostGisCopyTo
   :members:
   :undoc-members:

.. autoclass:: geoinf.postgis.PostGIS.reprojectPostGISTable
   :members:
   :undoc-members:

.. autoclass:: geoinf.postgis.PostGIS.SQLSourceConfigurationWidget
   :members:
   :undoc-members:


pgLoadersDumpers
----------------

.. automodule:: geoinf.postgis.pgLoadersDumpers
   :members:
   :undoc-members:

.. autoclass:: geoinf.postgis.pgLoadersDumpers.Shape2PostGIS
   :members:
   :undoc-members:


DataTransformations
-------------------

.. automodule:: geoinf.postgis.DataTransformations
   :members:
   :undoc-members:

.. autoclass:: geoinf.postgis.DataTransformations.InputStream
   :members:
   :undoc-members:

.. autoclass:: geoinf.postgis.DataTransformations.pgSQLMergeInsert
   :members:
   :undoc-members:


Web
===

.. automodule:: geoinf.web


Common
------

.. automodule:: geoinf.web.Common

.. autoclass:: geoinf.web.Common.OgcService
   :members:
   :undoc-members:

FTP
---

.. automodule:: geoinf.web.FTP

.. autoclass:: geoinf.web.FTP.FTPReader
   :members:
   :undoc-members:

OgcConfigurationWidget
----------------------

.. automodule:: geoinf.web.OgcConfigurationWidget

.. autoclass:: geoinf.web.OgcConfigurationWidget.OgcCommonWidget
   :members:
   :undoc-members:

.. autoclass:: geoinf.web.OgcConfigurationWidget.OgcConfigurationWidget
   :members:
   :undoc-members:

OgcService
----------

.. automodule:: geoinf.web.OgcService

.. autoclass:: geoinf.web.OgcService.OGC
   :members:
   :undoc-members:


PortConfigurationWidget
-----------------------

.. automodule:: geoinf.web.PortConfigurationWidget

.. autoclass:: geoinf.web.PortConfigurationWidget.Port
   :members:
   :undoc-members:

.. autoclass:: geoinf.web.PortConfigurationWidget.PortConfigurationWidget
   :members:
   :undoc-members:


SOS
------

.. automodule:: geoinf.web.SOS

.. autoclass:: geoinf.web.SOS.SOS
   :members:
   :undoc-members:

.. autoclass:: geoinf.web.SOS.SosCommonWidget
   :members:
   :undoc-members:

.. autoclass:: geoinf.web.SOS.SOSConfigurationWidget
   :members:
   :undoc-members:

SOSFeeder
---------

.. automodule:: geoinf.web.SOSFeeder

.. autoclass:: geoinf.web.SOS.SOS
   :members:
   :undoc-members:

.. autoclass:: geoinf.web.SOSFeeder.SOSFeeder
   :members:
   :undoc-members:

.. autoclass:: geoinf.web.SOSFeeder.InsertObservation
   :members:
   :undoc-members:

.. autoclass:: geoinf.web.SOSFeeder.RegisterSensor
   :members:
   :undoc-members:


WCS
----

.. automodule:: geoinf.web.WCS

.. autoclass:: geoinf.web.WCS.WCS
   :members:
   :undoc-members:

.. autoclass:: geoinf.web.WCS.WCSCommonWidget
   :members:
   :undoc-members:

.. autoclass:: geoinf.web.WCS.WCSConfigurationWidget
   :members:
   :undoc-members:


WFS
----

.. automodule:: geoinf.web.WFS

.. autoclass:: geoinf.web.WFS.WFS
   :members:
   :undoc-members:

.. autoclass:: geoinf.web.WFS.WFSCommonWidget
   :members:
   :undoc-members:

.. autoclass:: geoinf.web.WFS.WFSConfigurationWidget
   :members:
   :undoc-members:


WPS
----

.. automodule:: geoinf.web.WPS
   :members:

.. autoclass:: geoinf.web.WPS.WPS
   :members:
   :undoc-members:

.. autoclass:: geoinf.web.WPS.WPSConfigurationWidget
   :members:
   :undoc-members:

.. autoclass:: geoinf.web.WPS.WPSMessageBox
   :members:
   :undoc-members:


..
    Common
    ------
    
    .. automodule:: geoinf.web.Common
    
    .. autoclass:: geoinf.web.Common.
       :members:
       :undoc-members:
    
    
    Common
    ------
    
    .. automodule:: geoinf.web.Common
    
    .. autoclass:: geoinf.web.Common.
       :members:
       :undoc-members:
