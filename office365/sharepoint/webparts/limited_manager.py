from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.webparts.definition_collection import WebPartDefinitionCollection


class LimitedWebPartManager(BaseEntity):
    """Provides operations to access and modify the existing Web Parts on a Web Part Page, and add new ones
    to the Web Part Page."""

    def web_parts(self):
        """A collection of the Web Parts on the Web Part Page available to the current user based
        on the current user’s permissions."""
        return self.properties.get('WebParts',
                                   WebPartDefinitionCollection(self.context,
                                                               ResourcePath("WebParts", self.resource_path)))

    @property
    def entity_type_name(self):
        return "SP.WebParts.LimitedWebPartManager"

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "WebParts": self.web_parts
            }
            default_value = property_mapping.get(name, None)
        return super(LimitedWebPartManager, self).get_property(name, default_value)
