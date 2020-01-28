from office365.runtime.resource_path import ResourcePath


class ResourcePathEntity(ResourcePath):
    """Resource path for addressing a Collection (of Entities),
    a single entity within a Collection,as well as a property of an entity"""

    def __init__(self, context, parent, entity_name):
        super(ResourcePathEntity, self).__init__(context, parent)
        self._entity_name = entity_name

    @property
    def segment(self):
        return self._entity_name

    @staticmethod
    def from_uri(uri, context):
        """Constructs aan instance of ResourcePathEntity from uri"""
        if uri.startswith(context.serviceRootUrl):
            uri = uri[len(context.serviceRootUrl):]
        segments = uri.split('/')
        parent = None
        for segment in segments:
            parent = ResourcePathEntity(context, parent, segment)
        return parent
