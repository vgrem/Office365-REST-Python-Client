from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class ConfiguredMetadataNavigationItem(ClientValue):
    """Represents a configured metadata navigation item."""

    def __init__(self, field_display_name=None):
        """
        :param str field_display_name: The display name of the field that this item refers to.
        """
        self.FieldDisplayName = field_display_name


class ConfiguredMetadataNavigationItemCollection(ClientValue):
    """A collection of configured metadata navigation items."""

    def __init__(self, items=None):
        self.Items = ClientValueCollection(ConfiguredMetadataNavigationItem, items)
