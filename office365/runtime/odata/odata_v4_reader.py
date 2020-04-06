import xml.etree.ElementTree as ET
from abc import ABC

from office365.runtime.odata.odata_base_reader import ODataBaseReader
from office365.runtime.odata.odata_model import ODataModel


class ODataV4Reader(ODataBaseReader):
    """OData v4 reader"""
    _options = None

    def __init__(self, options):
        super().__init__(options)
        self._options['namespaces'] = {
            'xmlns': 'http://docs.oasis-open.org/odata/ns/edm',
            'edmx': 'http://docs.oasis-open.org/odata/ns/edmx'
        }

    def process_type_node(self, model, type_schema, type_node):
        for prop_node in type_node.findall('xmlns:Property', self._options['namespaces']):
            name = prop_node.get('Name')
            prop_schema = {'name': name}
            model.resolve_property(type_schema, prop_schema)
