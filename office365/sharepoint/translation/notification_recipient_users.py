from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class TranslationNotificationRecipientUsers(BaseEntity):

    @property
    def language_code(self):
        return self.properties.get("LanguageCode", None)

    @property
    def recipients(self):
        from office365.sharepoint.principal.users.collection import UserCollection
        return self.properties.get("Recipients",
                                   UserCollection(self.context, ResourcePath("Recipients", self.resource_path)))
