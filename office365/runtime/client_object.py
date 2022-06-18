import copy
import datetime
from typing import TypeVar

from office365.runtime.client_value import ClientValue
from office365.runtime.odata.odata_type import ODataType
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_json_format import ODataJsonFormat
from office365.runtime.odata.query_options import QueryOptions

T = TypeVar('T', bound='ClientObject')
P_T = TypeVar('P_T')


class ClientObject(object):

    def __init__(self, context, resource_path=None, parent_collection=None, namespace=None):
        """
        Base client object which define named properties and relationships of an entity

        :type parent_collection: office365.runtime.client_object_collection.ClientObjectCollection or None
        :type resource_path: office365.runtime.paths.resource_path.ResourcePath or None
        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        :type namespace: str
        """
        self._properties = {}
        self._properties_metadata = {}
        self._entity_type_name = None
        self._query_options = QueryOptions()
        self._parent_collection = parent_collection
        self._context = context
        self._resource_path = resource_path
        self._namespace = namespace

    def set_metadata(self, name, group, value):
        if name not in self._properties_metadata:
            self._properties_metadata[name] = {}
        self._properties_metadata[name][group] = value

    def get_metadata(self, name, group, default_value=None):
        return self._properties_metadata.get(name, {}).get(group, default_value)

    def clear(self):
        self._properties_metadata = {}

    def execute_query(self):
        """
        Submit request(s) to the server

        :type self: T
        """
        self.context.execute_query()
        return self

    def execute_query_retry(self, max_retry=5,
                            timeout_secs=5,
                            success_callback=None,
                            failure_callback=None):
        self.context.execute_query_retry(max_retry=max_retry,
                                         timeout_secs=timeout_secs,
                                         success_callback=success_callback,
                                         failure_callback=failure_callback)
        return self

    def build_request(self):
        return self.context.build_request(self.context.current_query)

    def get(self):
        """Retrieves a client object from the server

        :type self: T
        """
        self.context.load(self)
        return self

    def is_property_available(self, name):
        """Returns a Boolean value that indicates whether the specified property has been retrieved or set.

        :param str name: A property name
        """
        if name in self.properties:
            return True
        return False

    def expand(self, names):
        """
        Specifies the related resources to be included in line with retrieved resources

        :type self: T
        :type names: list[str]
        """
        self.query_options.expand = names
        return self

    def select(self, names):
        """
        Allows to request a limited set of properties

        :type self: T
        :param list[str] names: the list of property names
        """
        self.query_options.select = names
        return self

    def remove_from_parent_collection(self):
        if self._parent_collection is None:
            return
        self._parent_collection.remove_child(self)
        return self

    def get_property(self, name, default_value=None):
        """
        Gets property value

        :type name: str
        :type default_value: P_T
        :rtype: P_T
        """
        if default_value is None:
            normalized_name = name[0].lower() + name[1:]
            default_value = getattr(self, normalized_name, None)
        return self._properties.get(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        """Sets property value

        :param str name: Property name
        :param P_T value: Property value
        :param bool persist_changes: Persist changes
        """
        self._properties_metadata[name] = {}
        if persist_changes:
            self.set_metadata(name, "persist", True)

        prop_type = self.get_property(name)
        if isinstance(prop_type, ClientObject) or isinstance(prop_type, ClientValue):
            if isinstance(value, list):
                [prop_type.set_property(i, v, persist_changes) for i, v in enumerate(value)]
                self._properties[name] = prop_type
            elif isinstance(value, dict):
                [prop_type.set_property(k, v, persist_changes) for k, v in value.items()]
                self._properties[name] = prop_type
            else:
                self._properties[name] = value
        else:
            if isinstance(prop_type, datetime.datetime):
                self._properties[name] = ODataType.parse_datetime(value)
            else:
                self._properties[name] = value
        return self

    def ensure_property(self, name, action, *args, **kwargs):
        """
        Ensures if property is loaded

        :type action: () -> None
        :type name: str
        """
        return self.ensure_properties([name], action, *args, **kwargs)

    def ensure_properties(self, names, action, *args, **kwargs):
        """
        Ensure if list of properties are loaded

        :type action: (any) -> None
        :type names: str or list[str]
        """

        names_to_include = [n for n in names if not self.is_property_available(n)]
        if len(names_to_include) > 0:
            from office365.runtime.queries.read_entity import ReadEntityQuery
            qry = ReadEntityQuery(self, names_to_include)
            self.context.add_query(qry, set_as_current=False)
            self.context.after_query_execute(qry, action, *args, **kwargs)
        else:
            action(*args, **kwargs)
        return self

    def clone_object(self):
        """Clones a client object"""
        result = copy.deepcopy(self)
        result._context = self.context
        return result

    @property
    def entity_type_name(self):
        """Returns server type name"""
        if self._entity_type_name is None:
            if self._namespace is None:
                self._entity_type_name = type(self).__name__
            else:
                self._entity_type_name = ".".join([self._namespace, type(self).__name__])
        return self._entity_type_name

    @property
    def resource_url(self):
        """
        Returns resource url

        :rtype: str or None
        """
        if self.resource_path is None:
            return None
        return self.context.service_root_url() + str(self.resource_path)

    @property
    def context(self):
        return self._context

    @property
    def resource_path(self):
        return self._resource_path

    @property
    def query_options(self):
        return self._query_options

    @property
    def properties(self):
        return self._properties

    @property
    def parent_collection(self):
        return self._parent_collection

    def to_json(self, json_format=None):
        """
        Serializes client object

        :type json_format: office365.runtime.odata.odata_json_format.ODataJsonFormat or None
        """
        if json_format is None:
            ser_prop_names = [n for n in self._properties.keys()]
            include_control_info = False
        else:
            ser_prop_names = [n for n, p in self._properties_metadata.items() if p.get("persist", False) is True]
            include_control_info = self.entity_type_name is not None and json_format.include_control_information()

        json = {k: self.get_property(k) for k in self._properties if k in ser_prop_names}
        for k, v in json.items():
            if isinstance(v, ClientObject) or isinstance(v, ClientValue):
                json[k] = v.to_json(json_format)

        if json and include_control_info:
            if isinstance(json_format, JsonLightFormat):
                json[json_format.metadata_type_tag_name] = {'type': self.entity_type_name}
            elif isinstance(json_format, ODataJsonFormat):
                json[json_format.metadata_type_tag_name] = "#" + self.entity_type_name
        return json
