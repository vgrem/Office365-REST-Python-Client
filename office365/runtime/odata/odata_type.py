class ODataType(object):

    primitive_types = {
        bool: "Edm.Boolean",
        int: "Edm.Int32",
        str: "Edm.String",
    }
    """Primitive server types"""

    def __init__(self):
        self.name = None
        self.namespace = None
        self.baseType = None
        self.properties = {}
        self.methods = {}

    def add_property(self, prop_schema):
        """
        :type prop_schema:  office365.runtime.odata.odata_property.ODataProperty
        """
        alias = prop_schema.name
        #if type_schema['state'] == 'detached':
        #    prop_schema['state'] = 'detached'
        #else:
        #    prop_schema['state'] = 'attached'
        #type_alias = type_schema['name']
        self.properties[alias] = prop_schema
