import xml.etree.ElementTree as ET

from office365.runtime.odata.odata_model import ODataModel


class ODataV4Reader(object):
    """OData v4 reader"""
    _options = None

    def __init__(self, options):
        self._options = options

    def generate_model(self):
        xml_namespaces = {
            'xmlns': 'http://docs.oasis-open.org/odata/ns/edm',
            'edmx': 'http://docs.oasis-open.org/odata/ns/edmx'
        }
        model = ODataModel()
        root = ET.parse(self._options['inputPath']).getroot()
        schema_node = root.find('edmx:DataServices/xmlns:Schema', xml_namespaces)
        for complex_type_node in schema_node.findall('xmlns:ComplexType', xml_namespaces):
            type_schema = {'namespace': schema_node.attrib['Namespace'], 'name': complex_type_node.get('Name')}
            model.resolve_type(type_schema)
            self._process_property_node(type_schema, complex_type_node)
        return model

    def _process_property_node(self, type_schema, type_node):
        type_schema['properties'] = {}
