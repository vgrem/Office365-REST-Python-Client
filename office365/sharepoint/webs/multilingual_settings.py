from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.translation.notification_recipient_users import TranslationNotificationRecipientUsers


class MultilingualSettings(BaseEntity):

    @property
    def recipients(self):
        return self.properties.get('Recipients',
                                   BaseEntityCollection(self.context, TranslationNotificationRecipientUsers,
                                                        ResourcePath("Recipients", self.resource_path)))
