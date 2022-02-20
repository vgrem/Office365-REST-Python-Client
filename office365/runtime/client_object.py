import copy

from office365.runtime.client_value import ClientValue
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_json_format import ODataJsonFormat
from office365.runtime.odata.query_options import QueryOptions


class ClientObject(object):

    def __init__(self, context, resource_path=None, parent_collection=None, namespace=None):
        """
        Base client object which define named properties and relationships of an entity

        :type parent_collection: office365.runtime.client_object_collection.ClientObjectCollection or None
        :type resource_path: office365.runtime.client_path.ClientPath or None
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
        self.context.load(self)
        return self

    def is_property_available(self, name):
        """Returns a Boolean value that indicates whether the specified property has been retrieved or set.

        :param str name: A Property name
        """
        if name in self.properties:
            return True
        return False

    def expand(self, names):
        """

        :type names: list[str]
        """
        self.query_options.expand = names
        return self

    def select(self, names):
        """

        :param list[str] names:
        :return:
        """
        self.query_options.select = names
        return self

    def remove_from_parent_collection(self):
        if self._parent_collection is None:
            return
        self._parent_collection.remove_child(self)

    def get_property(self, name, default_value=None):
        """
        Gets property value

        :param str name: property name
        :param any default_value: property value
        """
        if default_value is None:
            normalized_name = name[0].lower() + name[1:]
            default_value = getattr(self, normalized_name, None)
        return self._properties.get(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        """Sets property value

        :param str name: Property name
        :param any value: Property value
        :param bool persist_changes: Persist changes
        """
        self._properties_metadata[name] = {}
        if persist_changes:
            self.set_metadata(name, "persist", True)

        prop_type = self.get_property(name)
        if isinstance(prop_type, ClientObject) or isinstance(prop_type, ClientValue) and value is not None:
            if isinstance(value, list):
                [prop_type.set_property(i, v, persist_changes) for i, v in enumerate(value)]
                self._properties[name] = prop_type
            elif isinstance(value, dict):
                [prop_type.set_property(k, v, persist_changes) for k, v in value.items()]
                self._properties[name] = prop_type
            else:
                self._properties[name] = value
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
            from office365.runtime.queries.read_entity_query import ReadEntityQuery
            qry = ReadEntityQuery(self, names_to_include)
            self.context.add_query(qry, set_as_current=False)
            self.context.after_query_execute(qry, action, *args, **kwargs)
        else:
            action(*args, **kwargs)
        return self

    def clone_object(self):
        result = copy.deepcopy(self)
        result._context = self.context
        return result

    @property
    def entity_type_name(self):
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
        :type json_format: office365.runtime.odata.odata_json_format.ODataJsonFormat or None
        """
        ser_prop_names = [n for n, p in self._properties_metadata.items() if p.get("persist", False) is True]
        json = dict((k, self.get_property(k)) for k in self.properties if k in ser_prop_names)
        for k, v in json.items():
            if isinstance(v, ClientObject) or isinstance(v, ClientValue):
                json[k] = v.to_json(json_format)

        if json and self.entity_type_name is not None and json_format.include_control_information():
            if isinstance(json_format, JsonLightFormat):
                json[json_format.metadata_type_tag_name] = {'type': self.entity_type_name}
            elif isinstance(json_format, ODataJsonFormat):
                json[json_format.metadata_type_tag_name] = "#" + self.entity_type_name
        return json
