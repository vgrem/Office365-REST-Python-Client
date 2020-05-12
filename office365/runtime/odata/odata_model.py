from pydoc import locate


class ODataModel(object):
    """OData model"""
    _types = {}
    _namespaces = ['directory', 'onedrive', 'outlookservices', 'teams']

    def resolve_type(self, schema):
        type_alias = schema['name']
        types = [locate("office365.{0}.{1}".format(ns, type_alias)) for ns in self._namespaces]
        found_modules = [t for t in types if t is not None]
        if any(found_modules):
            schema['state'] = 'attached'
            schema['file'] = found_modules[0].__file__
        else:
            schema['state'] = 'detached'
        schema['properties'] = {}
        self._types[type_alias] = schema

    def resolve_property(self, type_schema, prop_schema):
        alias = prop_schema['name']
        if type_schema['state'] == 'detached':
            prop_schema['state'] = 'detached'
        else:
            prop_schema['state'] = 'attached'
        type_alias = type_schema['name']
        self._types[type_alias]['properties'][alias] = prop_schema
