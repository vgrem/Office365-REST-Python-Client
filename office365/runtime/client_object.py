import importlib
from urllib3.util import parse_url

from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel
from office365.runtime.resource_path_entry import ResourcePathEntry


class ClientObject(object):
    """Base client object"""

    def __init__(self, context, resource_path=None, properties=None):
        if properties is None:
            properties = {}
        self._entity_type_name = None
        self._query_options = {}
        self._parent_collection = None
        self._context = context
        self._properties = properties
        self._metadata = {}
        self._changed_properties = properties
        self._resource_path = resource_path
        self._url = None
        self._use_custom_mapper = False

    @property
    def use_custom_mapper(self):
        return self._use_custom_mapper

    @use_custom_mapper.setter
    def use_custom_mapper(self, value):
        self._use_custom_mapper = value

    @property
    def include_metadata(self):
        if self.context.json_format.metadata == ODataMetadataLevel.Verbose:
            return True
        return False

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

    def create_typed_object(self, properties, client_object_type=None):
        from office365.sharepoint.client_context import ClientContext

        if client_object_type is None:
            # get type from metadata; the form is 'SP.ObjectType'
            client_object_type_name = properties["__metadata"]["type"][3:]

            if isinstance(self.context, ClientContext):
                module_name = self.context.__module__.replace("client_context", "") + client_object_type_name.lower()
            else:
                module_name = self.context.__module__.replace("outlook_client", "") + client_object_type_name.lower()

            try:
                lib = importlib.import_module(module_name)
                client_object_type = getattr(lib, client_object_type_name)
            except ModuleNotFoundError:
                raise ModuleNotFoundError("No class for object type '{0}' found".format(client_object_type_name))

        web_url, resource_path = properties["__metadata"]["uri"].split("/_api/")

        context = self.context
        if client_object_type.__name__ == "Web":
            # create a new context to represent the new web object
            context = ClientContext(web_url, self.context.auth_context)

        client_object = client_object_type(context, ResourcePathEntry.from_uri(resource_path, self.context))
        client_object.map_json(properties)

        return client_object

    def remove_from_parent_collection(self):
        if self._parent_collection is None:
            return
        self._parent_collection.remove(self)

    def is_property_available(self, name):
        """Returns a Boolean value that indicates whether the specified property has been retrieved or set."""
        if name in self.properties and (not isinstance(self.properties[name], dict) or '__deferred' not in self.properties[name]):
            return True
        return False

    def query_options_to_url(self):
        """Convert query options to url"""
        return '&'.join(['$%s=%s' % (key, value) for (key, value) in self.query_options.items()])

    def set_property(self, name, value, persist_changes=True):
        """Set resource property"""
        if persist_changes:  # persist properties
            self._changed_properties[name] = value
        self._properties[name] = value

    @property
    def context(self):
        return self._context

    @property
    def service_root_url(self):
        return self.context.service_root_url

    @property
    def resource_path(self):
        if self._resource_path:
            return self._resource_path

        url_parsed = parse_url(self._metadata.get("uri", ""))
        if url_parsed.path:
            self._resource_path = ResourcePathEntry.from_uri(
                url_parsed.path[url_parsed.path.rfind("/_api/")+6:], self._context)

        return self._resource_path

    @property
    def query_options(self):
        return self._query_options

    def expand(self, value):
        self.query_options['expand'] = value
        return self

    def select(self, value):
        self.query_options['select'] = value
        return self

    @property
    def url(self):
        if self._url:
            return self._url
        elif self.resource_path:
            self._url = self.service_root_url + self.resource_path.build_path_url()
            if self.query_options:
                self._url = self._url + "?" + self.query_options_to_url()
        elif self._metadata and 'uri' in self._metadata:
            self._url = self._metadata['uri']
        return self._url

    @property
    def type_name(self):
        return self.__module__ + "." + self.__class__.__name__

    @property
    def properties(self):
        return self._properties

    def convert_to_payload(self):
        """Generates resource payload for REST endpoint"""
        payload = dict(self._changed_properties)
        if self.include_metadata:
            self.ensure_metadata_type(payload)
        else:
            payload = dict((k, v) for k, v in payload.items() if k != "__metadata")
        return payload

    def map_json(self, payload):
        self._metadata = payload.get('__metadata')
        self._properties = dict((k, v) for k, v in payload.items()
                                if k != '__metadata')
