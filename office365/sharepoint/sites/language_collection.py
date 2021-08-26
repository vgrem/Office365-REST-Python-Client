from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sites.language import Language


class LanguageCollection(BaseEntity):

    def __init__(self, context, resource_path=None):
        super(LanguageCollection, self).__init__(context, resource_path)
        self.properties["Items"] = ClientValueCollection(Language)

    @property
    def items(self):
        """
        :rtype: ClientValueCollection
        """
        return self.properties.get("Items")

    def set_property(self, name, value, persist_changes=True):
        self.items.set_property(name, value, persist_changes)
        return self
