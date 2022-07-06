from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sites.language import Language


class LanguageCollection(BaseEntity):

    def __init__(self, context, resource_path=None):
        """Represents a collection of SPLanguage objects."""
        super(LanguageCollection, self).__init__(context, resource_path)
        self.properties["Items"] = ClientValueCollection(Language)

    @property
    def items(self):
        return self.properties.get("Items", ClientValueCollection(Language))

    def __repr__(self):
        return repr(self.items)

    def set_property(self, name, value, persist_changes=True):
        self.items.set_property(name, value, persist_changes)
        return self
