from office365.runtime.resource_path import ResourcePath


class ResourcePathEntity(ResourcePath):
    """Resource path for addressing a Collection (of Entities),
    a single entity within a Collection,as well as a property of an entity"""

    def __init__(self, context, parent, entity_name):
        super(ResourcePathEntity, self).__init__(context, parent)
        self._entity_name = entity_name

    @property
    def url(self):
        return self._entity_name

    @staticmethod
    def from_uri(uri, context):
        """Constructs aan instance of ResourcePathEntity from uri"""
        if uri.startswith(context.service_root_url):
            uri = uri[len(context.service_root_url):]
        elements = uri.split('/')
        parent = None
        for element in elements:
            parent = ResourcePathEntity(context, parent, element)
        return parent
