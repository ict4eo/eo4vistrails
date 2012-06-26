from osgeo import ogr
import csv as csv
from Parser import Parser

CSV_OUT = "/tmp/sos.csv"  # need to use VisTrails temp file

def get_csv(SOS_XML_file, output_file=None, delimiter=',', header=True,
            missing_value=None, quotechar='"'):
    """Create a CSV with time series data."""
    results = extract_time_series(SOS_XML_file)  # get data and metadata
    for index, result in enumerate(results):
        file_out = output_file or CSV_OUT
        if index > 0:
            file_out = file_out + '_' + str(index)
        f_out = open(file_out, "w")
        if quotechar:
            quoting=csv.QUOTE_NONNUMERIC
        else:
            quoting=csv.QUOTE_MINIMAL
        csv_writer = csv.writer(open(file_out, "w"),
                                delimiter=delimiter,
                                quotechar=quotechar,
                                quoting=quoting)
        if header:
            common = ['Observation','Feature',  'Sample Point', 'Geometry']
            for field in result['fields']:
                _field = field['name']
                if field['units']:
                    _field += ' (' + field['units'] + ')'
                common.append(_field)
            csv_writer.writerow(common)
        # write to file
        for index, datum in enumerate(result['data']):
            datum.insert(0, result['feature']['geometry'])
            datum.insert(0, result['sampling_point']['id'])
            datum.insert(0, result['feature']['id'])
            datum.insert(0, result['observation']['id'])
            csv_writer.writerow(datum)

def get_fields(thefile):
    """Parse a SOS GML file and extract the field data."""
    doc = Parser(file=thefile, namespace="http://www.opengis.net/swe/1.0.1")
    om_result = doc.tag('member/Observation/result', doc.get_ns('om'))
    fields = doc.elem_tags(
        om_result,
        'DataArray/elementType/DataRecord/field')
    return extract_field_data(doc, fields)

def get_bounds(thefile):
    """Parse a SOS GML file and extract bounding box as a tuple."""
    doc = Parser(file=thefile, namespace="http://www.opengis.net/gml")
    try:
        bnd_up = doc.tag_value('boundedBy/Envelope/upperCorner').split()
        bnd_lo = doc.tag_value('boundedBy/Envelope/lowerCorner').split()
        return (bnd_up + bnd_up)
    except:
        return []

def extract_field_data(doc, fields):
    """Return a data dictionary from a SOS XML field element."""
    field_list = []
    if fields:
        for index, field in enumerate(fields):
            field_set = {}
            name = doc.elem_attr_value(field, 'name')
            units = None
            if len(field) > 0:  # no.of nodes
                child = field[0]  # first child; Time/Quantity/Text/Category
                defn = doc.elem_attr_value(child, 'definition')
                field_set['definition'] = defn
                field_set['name'] = name or defn
                # units
                uom = doc.elem_tag(child, 'uom')
                field_set['units'] = doc.elem_attr_value(uom, 'code') or ''
            field_list.append(field_set)
    return field_list

def extract_time_series(thefile):
    """Parse a SOS GML file and extract time series and other meta data."""
    doc = Parser(file=thefile, namespace="http://www.opengis.net/swe/1.0.1")
    results = []
    om_members = doc.tags('member', doc.get_ns('om'))
    for om_member in om_members:
        om_obs = doc.elem_tag(om_member,
                              'Observation',
                              doc.get_ns('om'))
        # look for an observation id
        observation = {}
        id = doc.elem_attr_value(om_obs, 'href', doc.get_ns('xlink'))
        if not id:
            id = doc.elem_attr_value(om_obs, 'id', doc.get_ns('gml'))
        observation['id'] = id
        # process results...
        om_obs_result = doc.elem_tag(om_member,
                                   'Observation/result',
                                   doc.get_ns('om'))
        if om_obs_result:
            result = {}
            # 'meta' data - feature information
            feature = {}
            om_feature = doc.elem_tag(om_member,
                                    'Observation/featureOfInterest',
                                    doc.get_ns('om'))
            # look for a feature id
            id = doc.elem_attr_value(om_feature, 'href', doc.get_ns('xlink'))
            if not id:
                id = doc.elem_attr_value(om_feature, 'id', doc.get_ns('gml'))
            feature['id'] = id
            feature['name'] = None  # attempt to find a name ...???
            # get feature geomtry
            om_point= doc.elem_tag_nested(om_feature,
                                          'Point',
                                          doc.get_ns('gml'))
            if om_point:
                geom_wkt = None
                geom_value = doc.elem_tag_value(om_point[0],
                                                'pos',
                                                doc.get_ns('gml'))
                if not geom_value:
                    geom_value = doc.elem_tag_value(om_point,
                                                    'coordinates',
                                                    doc.get_ns('gml'))
                """                """
                if geom_value:
                    #print geom_value[0], geom_value
                    points = geom_value.split(' ')
                    point = ogr.Geometry(ogr.wkbPoint)
                    point.AddPoint(float(points[0]), float(points[1]))
                    #print geom_value[0], geom_value[1]
                    #point.AddPoint(10.23, 36.6)
                    geom_wkt  = point.ExportToWkt()  # WKT format

                feature['geometry'] = geom_wkt

            else:
                feature['geometry'] = None
            # look for a sample point id
            #   sa:SamplingPoint as a nested child ...
            sampling_point = {}
            om_sampling_point = doc.elem_tag_nested(om_feature,
                                                  'SamplingPoint',
                                                  doc.get_ns('sa'))
            print "125", om_sampling_point
            if om_sampling_point and len(om_sampling_point) == 1:
                id = doc.elem_attr_value(om_feature, 'xlink:href')
                if not id:
                    id = doc.elem_attr_value(om_sampling_point[0],
                                             'id',
                                             doc.get_ns('gml'))
            sampling_point['id'] = id
            # 'meta' data - field information
            fields = doc.elem_tags(
                om_obs_result,
                'DataArray/elementType/DataRecord/field')
            result['fields'] = extract_field_data(doc, fields)
            # data
            textblock = doc.elem_tag(
                om_obs_result,
                'DataArray/encoding/TextBlock')
            block = doc.elem_attr_value(textblock, 'blockSeparator')
            token = doc.elem_attr_value(textblock, 'tokenSeparator')
            value_list = []
            values = doc.elem_tag_value(om_obs_result, 'DataArray/values')
            if values:
                val_set = values.split(block)
                for val in val_set:
                    value_list.append(val.split(token))
            # store results
            result['observation'] = observation
            result['sampling_point'] = sampling_point
            result['feature'] = feature
            result['data'] = value_list
            #print "extract_time_series:133", result
            results.append(result)
    return results





    """
    print "TVL:172 - NS", p.namespace, '\n        - XML', p.xml
    print "TVL:173 - ObservationCollection", obs
    print "TVL:174 - ObservationCollection_gml:id", obs_id
    print "TVL:175 - Bounds", bounds
    print "TVL:176 - om:result", om_result
    print "TVL:177 - LEN swe:values", len(values)
    print "TVL:178 - swe:fields", fields
    print "TVL:179 - swe:Token", token, "swe:Block", block
    print "TVL:180 - swe:TextBlock", textblock, "LEN:", len(val_set)
    print "TVL:181 - fields", field_set
    """

print "test bounds", get_bounds('/home/dhohls/Desktop/sos_test.xml')
print "\n"
get_csv('/home/dhohls/Desktop/sos_test.xml', "/tmp/sosT.csv")

"""
print "\n"
get_csv('/home/dhohls/Desktop/sos_SADCO.xml', "/tmp/sosS.csv")
print "\n"
get_csv('/home/dhohls/Desktop/myfile.gml', "/tmp/sosG.csv")
"""
