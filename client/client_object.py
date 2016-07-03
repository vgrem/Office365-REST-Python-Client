import importlib


class ClientObject(object):
    """Base client object"""

    def __init__(self, context, resource_path=None, parent_resource_path=None, properties=None):
        if properties is None:
            properties = {}
        self._entity_type_name = None
        self._query_options = {}
        self._service_root_url = context.url + "/_api/"
        self._parent_collection = None
        self._context = context
        self._properties = properties
        self._changed_properties = properties
        self._resource_path = resource_path
        self._parent_resource_path = parent_resource_path
        self._url = None

    @property
    def entity_type_name(self):
        if self._entity_type_name is None:
            self._entity_type_name = "SP." + type(self).__name__
        return self._entity_type_name

    @entity_type_name.setter
    def entity_type_name(self, value):
        self._entity_type_name = value

    def ensure_metadata_type(self, entity):
        """Ensures metadata type is contained in payload"""
        if '__metadata' not in entity:
            entity["__metadata"] = {'type': self.entity_type_name}

    @staticmethod
    def create_typed_object(ctx, properties):
        typeParts = properties["__metadata"]["type"].split(".")
        class_name = typeParts[1]
        if len(typeParts) == 3:
            if typeParts[1] == "Data":
                class_name = "ListItem"
            else:
                class_name = typeParts[2]
        module_name = "client.{0}".format(class_name.lower())
        clientObjectClass = getattr(importlib.import_module(module_name), class_name)
        client_object = clientObjectClass(ctx)
        client_object.from_json(properties)
        return client_object

    def remove_from_parent_collection(self):
        if self._parent_collection is None:
            return
        self._parent_collection.remove(self)

    def is_property_available(self, name):
        """Returns a Boolean value that indicates whether the specified property has been retrieved or set."""
        if name in self.properties and '__deferred' not in self.properties[name]:
            return True
        return False

    def query_options_to_url(self):
        """Convert query options to url"""
        return '&'.join(['$%s=%s' % (key, value) for (key, value) in self.query_options.items()])

    def set_property(self, name, value, persist_changes=True):
        """Set resource property"""
        if persist_changes:  # persist changed/updated properties
            self._changed_properties[name] = value
        self._properties[name] = value

    @property
    def context(self):
        return self._context

    @property
    def service_root_url(self):
        return self._service_root_url

    @property
    def resource_path(self):
        if self._parent_resource_path:
            return self._parent_resource_path + "/" + self._resource_path
        return self._resource_path

    @property
    def query_options(self):
        return self._query_options

    @property
    def url(self):
        if self._url:
            return self._url
        else:
            self._url = self.service_root_url + self.resource_path
        if self.query_options:
            self._url = self._url + "?" + self.query_options_to_url()
        return self._url

    @property
    def type_name(self):
        return self.__module__ + "." + self.__class__.__name__

    @property
    def properties(self):
        return self._properties

    def to_json(self):
        """Generates resource payload for REST endpoint"""
        json = dict(self._changed_properties)
        self.ensure_metadata_type(json)
        return json

    def from_json(self, json):
        self._properties = json
        if '__metadata' in self._properties:
            self._url = self._properties['__metadata']['uri']
            self._entity_type_name = self._properties['__metadata']['type']
