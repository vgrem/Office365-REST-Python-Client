from office365.runtime.odata.odata_base_reader import ODataBaseReader


class ODataV3Reader(ODataBaseReader):
    """OData v3 reader"""

    def __init__(self, options):
        super().__init__(options)
        self._options['namespaces'] = {
            'xmlns': 'http://schemas.microsoft.com/ado/2009/11/edm',
            'edmx': 'http://schemas.microsoft.com/ado/2007/06/edmx',
            'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata'
        }

    def process_type_node(self, model, type_schema, type_node):
        for prop_node in type_node.findall('xmlns:Property', self._options['namespaces']):
            name = prop_node.get('Name')
            prop_schema = {'name': name}
            model.resolve_property(type_schema, prop_schema)
