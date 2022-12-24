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
    def _try_parse_key_value(value):
        """
        :type value: dict
        """
        key = value.get('Key', None)
        type_name = value.get('ValueType', None)
        raw_value = value.get("Value", None)
        try:
            if type_name == 'Edm.Int64':
                return key, int(raw_value)
            elif type_name == 'Edm.Double':
                return key, float(raw_value)
            elif type_name == 'Edm.Boolean':
                return key, raw_value == "true"
            else:
                return key, raw_value
        except ValueError:
            return key, raw_value

    @staticmethod
    def parse_key_value_collection(value):
        """
        Converts the collection of SP.KeyValue into dict

        :type value: dict
        """
        result = {}
        for v in value.values():
            key, value = ODataType._try_parse_key_value(v)
            result[key] = value
        return result

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
