import xml.etree.ElementTree as ET

from office365.runtime.odata.odata_model import ODataModel


class ODataV4Reader(object):
    """OData v4 reader"""
    _options = None

    def __init__(self, options):
        self._options = options
        self._namespaces = {
            'xmlns': 'http://docs.oasis-open.org/odata/ns/edm',
            'edmx': 'http://docs.oasis-open.org/odata/ns/edmx'
        }

    def generate_model(self):
        model = ODataModel()
        root = ET.parse(self._options['inputPath']).getroot()
        schema_node = root.find('edmx:DataServices/xmlns:Schema', self._namespaces)
        for complex_type_node in schema_node.findall('xmlns:ComplexType', self._namespaces):
            type_schema = {'namespace': schema_node.attrib['Namespace'], 'name': complex_type_node.get('Name')}
            model.resolve_type(type_schema)
            self._process_type_node(model, type_schema, complex_type_node)
        return model

    def _process_type_node(self, model, type_schema, type_node):
        for prop_node in type_node.findall('xmlns:Property', self._namespaces):
            name = prop_node.get('Name')
            prop_schema = {'name': name}
            model.resolve_property(type_schema, prop_schema)
