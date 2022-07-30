import datetime
import uuid


class ODataType(object):

    primitive_types = {
        bool: "Edm.Boolean",
        int: "Edm.Int32",
        str: "Edm.String",
        datetime.datetime: "Edm.DateTimeOffset",
        uuid.UUID: "Edm.Guid"
    }
    """Primitive OData data type mapping"""

    def __init__(self):
        self.name = None
        self.namespace = None
        self.baseType = None
        self.properties = {}
        self.methods = {}

    @staticmethod
    def parse_datetime(value):
        """
        Converts the specified string representation of an Edm.DateTime to its datetime equivalent

        :param str value: Represents date and time with values ranging from 12:00:00 midnight, January 1, 1753 A.D.
            through 11:59:59 P.M, December 9999 A.D.
        """
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            return None

    @staticmethod
    def resolve_type(client_type):
        """
        Resolves OData type name

        :param T client_type: Client value type
        """
        from office365.runtime.client_value import ClientValue
        if issubclass(client_type, ClientValue):
            client_value = client_type()
            return client_value.entity_type_name
        else:
            return ODataType.primitive_types.get(client_type, None)

    def add_property(self, prop_schema):
        """
        :type prop_schema:  office365.runtime.odata.property.ODataProperty
        """
        alias = prop_schema.name
        # if type_schema['state'] == 'detached':
        #    prop_schema['state'] = 'detached'
        # else:
        #    prop_schema['state'] = 'attached'
        # type_alias = type_schema['name']
        self.properties[alias] = prop_schema
