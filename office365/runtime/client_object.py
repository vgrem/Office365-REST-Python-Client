import datetime
from typing import TypeVar

from office365.runtime.client_value import ClientValue
from office365.runtime.odata.type import ODataType
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.odata.json_format import ODataJsonFormat
from office365.runtime.odata.query_options import QueryOptions

T = TypeVar('T', bound='ClientObject')
P_T = TypeVar('P_T')


class ClientObject(object):

    def __init__(self, context, resource_path=None, parent_collection=None):
        """
        Base client object which define named properties and relationships of an entity

        :type parent_collection: office365.runtime.client_object_collection.ClientObjectCollection or None
        :type resource_path: office365.runtime.paths.resource_path.ResourcePath or None
        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        """
        self._properties = {}
        self._ser_property_names = []
        self._query_options = QueryOptions()
        self._parent_collection = parent_collection
        self._context = context
        self._entity_type_name = None
        self._resource_path = resource_path

    def clear(self):
        """
        Resets client object's state
        """
        self._properties = {k: v for k, v in self._properties.items() if k not in self._ser_property_names}
        self._ser_property_names = []
        self._query_options = QueryOptions()
        return self

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
        """
        Executes the current set of data retrieval queries and method invocations and retries it if needed.

        :param int max_retry: Number of times to retry the request
        :param int timeout_secs: Seconds to wait before retrying the request.
        :param (office365.runtime.client_object.ClientObject)-> None success_callback: A callback to call
            if the request executes successfully.
        :param (int, requests.exceptions.RequestException)-> None failure_callback: A callback to call if the request
            fails to execute
        """
        self.context.execute_query_retry(max_retry=max_retry,
                                         timeout_secs=timeout_secs,
                                         success_callback=success_callback,
                                         failure_callback=failure_callback)
        return self

    def after_execute(self, action, *args, **kwargs):
        """
        Attach an event handler to client object which gets triggered after query is submitted to server
        """
        self._context.after_query_execute(action, self, *args, **kwargs)
        return self

    def get(self):
        """
        Retrieves a client object from the server
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

    def _persist_changes(self, name):
        """
        Marks a property as a serializable
        :param str name: A property name
        """
        if name not in self._ser_property_names:
            self._ser_property_names.append(name)
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
        if persist_changes:
            self._ser_property_names.append(name)

        typed_value = self.get_property(name)
        if isinstance(typed_value, ClientObject) or isinstance(typed_value, ClientValue):
            if isinstance(value, list):
                [typed_value.set_property(i, v, persist_changes) for i, v in enumerate(value)]
                self._properties[name] = typed_value
            elif isinstance(value, dict):
                [typed_value.set_property(k, v, persist_changes) for k, v in value.items()]
                self._properties[name] = typed_value
            else:
                self._properties[name] = value
        else:
            if isinstance(typed_value, datetime.datetime):
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
        Ensure if list of properties are retrieved from the server

        :type action: (any) -> None
        :type names: str or list[str]
        """

        names_to_include = [n for n in names if not self.is_property_available(n)]
        if self.property_ref_name is not None and self.property_ref_name not in names_to_include:
            names_to_include.append(self.property_ref_name)
        if len(names_to_include) > 0:
            from office365.runtime.queries.read_entity import ReadEntityQuery
            qry = ReadEntityQuery(self, names_to_include)
            self.context.add_query(qry).after_query_execute(action, *args, **kwargs)
        else:
            action(*args, **kwargs)
        return self

    @property
    def entity_type_name(self):
        """Returns server type name for an entity"""
        if self._entity_type_name is None:
            self._entity_type_name = type(self).__name__
        return self._entity_type_name

    @property
    def property_ref_name(self):
        """Returns property reference name

        :rtype: str
        """
        return None

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
        """Parent collection"""
        return self._parent_collection

    def to_json(self, json_format=None):
        """
        Serializes client object

        :type json_format: office365.runtime.odata.json_format.ODataJsonFormat or None
        """
        if json_format is None:
            ser_prop_names = [n for n in self._properties.keys()]
            include_control_info = False
        else:
            ser_prop_names = [n for n in self._ser_property_names]
            include_control_info = self.entity_type_name is not None and json_format.include_control_information

        json = {k: self.get_property(k) for k in self._properties if k in ser_prop_names}
        for k, v in json.items():
            if isinstance(v, ClientObject) or isinstance(v, ClientValue):
                json[k] = v.to_json(json_format)

        if json and include_control_info:
            if isinstance(json_format, JsonLightFormat):
                json[json_format.metadata_type] = {'type': self.entity_type_name}
            elif isinstance(json_format, ODataJsonFormat):
                json[json_format.metadata_type] = "#" + self.entity_type_name
        return json
