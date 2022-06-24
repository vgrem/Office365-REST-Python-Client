from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.translation.status import TranslationStatus


class TranslationStatusCollection(BaseEntity):

    def __init__(self, context, resource_path=None):
        super(TranslationStatusCollection, self).__init__(context, resource_path)

    @property
    def untranslated_languages(self):
        return self.properties.get("UntranslatedLanguages", StringCollection())

    @property
    def items(self):
        return self.properties.get("Items", ClientValueCollection(TranslationStatus))
