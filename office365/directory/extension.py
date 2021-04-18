from office365.entity import Entity
from office365.entity_collection import EntityCollection


class Extension(Entity):
    """An abstract type to support the OData v4 open type openTypeExtension."""
    pass


class ExtensionCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(ExtensionCollection, self).__init__(context, Extension, resource_path)

