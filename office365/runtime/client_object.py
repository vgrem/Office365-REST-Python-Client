from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel


class ClientObject(object):
    """Base client object"""

    def __init__(self, context, resource_path=None, properties=None):
        self._properties = {}
        self._properties_metadata = {}
        if properties is not None:
            for k, v in properties.items():
                self.set_property(k, v, True)
        self._entity_type_name = None
        self._query_options = {}
        self._parent_collection = None
        self._context = context
        self._resource_path = resource_path
        self._resource_url = None

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

    def remove_from_parent_collection(self):
        if self._parent_collection is None:
            return
        self._parent_collection.remove(self)

    def is_property_available(self, name):
        """Returns a Boolean value that indicates whether the specified property has been retrieved or set."""
        if name in self.properties and (
            not isinstance(self.properties[name], dict) or '__deferred' not in self.properties[name]):
            return True
        return False

    def query_options_to_url(self):
        """Convert query options to url"""
        return '&'.join(['$%s=%s' % (key, value) for (key, value) in self.query_options.items()])

    def set_property(self, name, value, persist_changes=True):
        """Set resource property value"""
        self._properties_metadata[name] = {'readonly': not persist_changes}
        self._properties[name] = value

    @property
    def context(self):
        return self._context

    @property
    def service_root_url(self):
        return self.context.service_root_url

    @property
    def resource_path(self):
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
    def resource_url(self):
        """Get resource Url"""
        if self._resource_url:
            return self._resource_url
        elif self.resource_path:
            self._resource_url = self.service_root_url + self.resource_path.build_path_url()
            if self.query_options:
                self._resource_url = self._resource_url + "?" + self.query_options_to_url()
        return self._resource_url

    @property
    def type_name(self):
        return self.__module__ + "." + self.__class__.__name__

    @property
    def properties(self):
        return self._properties

    @property
    def properties_metadata(self):
        return self._properties_metadata

    def map_json(self, payload):
        self._properties = dict((k, v) for k, v in payload.items()
                                if k != '__metadata')
