from __future__ import annotations

from typing import List, Optional

from typing_extensions import Self

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.translation.notifications.recipient_col import (
    TranslationNotificationRecipientCollection,
)
from office365.sharepoint.translation.notifications.recipient_set_request import (
    TranslationNotificationRecipientSetRequest,
)
from office365.sharepoint.translation.notifications.recipient_users import (
    TranslationNotificationRecipientUsers,
)


class MultilingualSettings(Entity):
    """ """

    def set_notification_recipients(
        self, notification_recipients: List[TranslationNotificationRecipientCollection]
    ) -> Self:
        """Args:
        notification_recipients (list):
        """
        request = TranslationNotificationRecipientSetRequest(
            ClientValueCollection(TranslationNotificationRecipientCollection, notification_recipients)
        )
        qry = ServiceOperationQuery(self, "SetNotificationRecipients", None, request)
        self.context.add_query(qry)
        return self

    @property
    def recipients(self) -> EntityCollection[TranslationNotificationRecipientUsers]:
        return self.properties.get(
            "Recipients",
            EntityCollection(
                self.context,
                TranslationNotificationRecipientUsers,
                ResourcePath("Recipients", self.resource_path),
            ),
        )

    @property
    def follow_lang_preference(self) -> Optional[bool]:
        """Gets the FollowLangPreference property"""
        return self.properties.get("FollowLangPreference", None)

    def set_follow_lang_preference(self, request: bool) -> Self:
        """SetFollowLangPreference operation.

        Args:
            request (bool):
                request parameter
        """
        qry = ServiceOperationQuery(self, "SetFollowLangPreference", None, {"request": request}, None, None)
        self.context.add_query(qry)
        return self
