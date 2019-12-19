class ODataModel(object):
    """OData model"""
    _types = {}

    def resolve_type(self, schema):
        type_name = schema['name']
        self._types[type_name] = schema
        pass
