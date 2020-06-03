from office365.runtime.client_value_object import ClientValueObject
from office365.runtime.odata.odata_query_options import QueryOptions


class ClientObject(object):

    def __init__(self, context, resource_path=None, properties=None, parent_collection=None):
        """
        Base client object

        :type parent_collection: office365.runtime.client_object_collection.ClientObjectCollection or None
        :type properties: dict or None
        :type resource_path: office365.runtime.resource_path.ResourcePath or None
        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        """
        self._properties = {}
        self._changes = []
        self._entity_type_name = None
        self._query_options = QueryOptions()
        self._parent_collection = parent_collection
        self._context = context
        self._resource_path = resource_path
        if properties is not None:
            for k, v in properties.items():
                self.set_property(k, v, True)

    def is_property_available(self, name):
        """Returns a Boolean value that indicates whether the specified property has been retrieved or set."""
        if name in self.properties:
            return True
        return False

    def expand(self, names):
        self.query_options.expand = names
        return self

    def select(self, names):
        self.query_options.select = names
        return self

    def remove_from_parent_collection(self):
        if self._parent_collection is None:
            return
        self._parent_collection.remove_child(self)

    def set_property(self, name, value, persist_changes=True):
        """Set resource property value"""
        if persist_changes:
            self._changes.append(name)

        safe_name = name[0].lower() + name[1:]
        if hasattr(self, safe_name):
            prop_type = getattr(self, safe_name)
            if isinstance(prop_type, ClientObject) or isinstance(prop_type, ClientValueObject):
                [prop_type.set_property(k, v, persist_changes) for k, v in value.items()]
                self._properties[name] = prop_type
            else:
                self._properties[name] = value
        else:
            self._properties[name] = value

    def to_json(self):
        return dict((k, v) for k, v in self.properties.items() if k in self._changes)

    def ensure_property(self, name, action):
        """
        Ensures property is loaded

        :type action: any
        :type name: str
        """
        if not self.is_property_available(name):
            self.context.load(self, [name])
            self.context.afterExecuteOnce += action
        else:
            action(self)

    @property
    def entity_type_name(self):
        if self._entity_type_name is None:
            self._entity_type_name = "SP." + type(self).__name__
        return self._entity_type_name

    @entity_type_name.setter
    def entity_type_name(self, value):
        self._entity_type_name = value

    @property
    def resource_url(self):
        """Generate resource Url"""
        if self.resource_path:
            url = self.context.service_root_url + self.resource_path.to_url()
            if not self.query_options.is_empty:
                url = url + "?" + self._query_options.to_url()
            return url
        return None

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
