import xml.etree.ElementTree as ET
from abc import abstractmethod

from office365.runtime.odata.odata_model import ODataModel


class ODataBaseReader(object):
    """OData reader"""

    def __init__(self, options):
        """

        :type options: dict
        """
        self._options = options

    @abstractmethod
    def process_type_node(self, model, type_schema, type_node):
        pass

    def generate_model(self):
        model = ODataModel()
        root = ET.parse(self._options['inputPath']).getroot()
        schema_node = root.find('edmx:DataServices/xmlns:Schema', self._options['namespaces'])
        for complex_type_node in schema_node.findall('xmlns:ComplexType', self._options['namespaces']):
            type_schema = {'namespace': schema_node.attrib['Namespace'],
                           'name': complex_type_node.get('Name'),
                           'baseType': 'ComplexType'}
            model.resolve_type(type_schema)
            self.process_type_node(model, type_schema, complex_type_node)
        return model
