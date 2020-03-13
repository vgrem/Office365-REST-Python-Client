from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel


class ClientObject(object):
    """Base client object"""

    def __init__(self, context, resource_path=None, properties=None):
        self._properties = {}
        self._metadata = {}
        self._entity_type_name = None
        self._query_options = {}
        self._parent_collection = None
        self._context = context
        self._resource_path = resource_path
        if properties is not None:
            for k, v in properties.items():
                self.set_property(k, v, True)

    def is_property_available(self, name):
        """Returns a Boolean value that indicates whether the specified property has been retrieved or set."""
        if name in self.properties and not (isinstance(self.properties[name], dict)
                                            and '__deferred' in self.properties[name]):
            return True
        return False

    def query_options_to_url(self):
        """Convert query options to url"""
        return '&'.join(['$%s=%s' % (key, value) for (key, value) in self.queryOptions.items()])

    def expand(self, value):
        self.queryOptions['expand'] = value
        return self

    def select(self, value):
        self.queryOptions['select'] = value
        return self

    def remove_from_parent_collection(self):
        if self._parent_collection is None:
            return
        self._parent_collection.remove_child(self)

    def set_property(self, name, value, persist_changes=True):
        """Set resource property value"""
        self._metadata[name] = {'persist_changes': persist_changes}
        self._properties[name] = value

    def map_json(self, json):
        [self.set_property(k, v, False) for k, v in json.items() if k != '__metadata']

    def to_json(self, data_format):
        json = dict((k, v) for k, v in self.properties.items()
                    if k in self._metadata and self._metadata[k]['persist_changes'] is True)
        if data_format.metadata == ODataMetadataLevel.Verbose and "__metadata" not in json.items():
            json["__metadata"] = {'type': self.entityTypeName}
        return json

    @property
    def entityTypeName(self):
        if self._entity_type_name is None:
            self._entity_type_name = "SP." + type(self).__name__
        return self._entity_type_name

    @entityTypeName.setter
    def entityTypeName(self, value):
        self._entity_type_name = value

    @property
    def resourceUrl(self):
        """Generate resource Url"""
        if self.resourcePath:
            url = self.context.serviceRootUrl + self.resourcePath.to_string()
            if self.queryOptions:
                url = url + "?" + self.query_options_to_url()
            return url
        return None

    @property
    def context(self):
        return self._context

    @property
    def resourcePath(self):
        return self._resource_path

    @property
    def queryOptions(self):
        return self._query_options

    @property
    def typeName(self):
        return self.__module__ + "." + self.__class__.__name__

    @property
    def properties(self):
        return self._properties
