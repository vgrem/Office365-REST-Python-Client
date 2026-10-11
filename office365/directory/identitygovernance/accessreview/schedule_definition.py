from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.identitygovernance.accessreview.instance import (
    AccessReviewInstance,
)
from office365.directory.identitygovernance.accessreview.schedule.settings import (
    AccessReviewScheduleSettings,
)
from office365.directory.identitygovernance.accessreview.scope import AccessReviewScope
from office365.directory.users.identity import UserIdentity
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.accessreview.notification_recipient_item import (
        AccessReviewNotificationRecipientItem,
    )
    from office365.directory.identitygovernance.accessreview.reviewer_scope import (
        AccessReviewReviewerScope,
    )
    from office365.directory.identitygovernance.accessreview.stage_settings import (
        AccessReviewStageSettings,
    )


class AccessReviewScheduleDefinition(Entity):
    @property
    def created_by(self) -> UserIdentity:
        """Gets the createdBy property"""
        return self.properties.get("createdBy", UserIdentity())

    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description_for_admins(self) -> Optional[str]:
        """Gets the descriptionForAdmins property"""
        return self.properties.get("descriptionForAdmins", None)

    @property
    def description_for_reviewers(self) -> Optional[str]:
        """Gets the descriptionForReviewers property"""
        return self.properties.get("descriptionForReviewers", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def instance_enumeration_scope(self) -> AccessReviewScope:
        """Gets the instanceEnumerationScope property"""
        return self.properties.get("instanceEnumerationScope", AccessReviewScope())

    @property
    def last_modified_date_time(self) -> datetime:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def scope(self) -> AccessReviewScope:
        """Gets the scope property"""
        return self.properties.get("scope", AccessReviewScope())

    @property
    def settings(self) -> AccessReviewScheduleSettings:
        """Gets the settings property"""
        return self.properties.get("settings", AccessReviewScheduleSettings())

    @property
    def status(self) -> Optional[str]:
        """Gets the status property"""
        return self.properties.get("status", None)

    @property
    def instances(self) -> EntityCollection[AccessReviewInstance]:
        """Gets the instances property"""
        return self.properties.get(
            "instances",
            EntityCollection[AccessReviewInstance](
                self.context, AccessReviewInstance, ResourcePath("instances", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessReviewScheduleDefinition"

    @property
    def additional_notification_recipients(self) -> ClientValueCollection[AccessReviewNotificationRecipientItem]:
        """Gets the additionalNotificationRecipients property"""
        from office365.directory.identitygovernance.accessreview.notification_recipient_item import (
            AccessReviewNotificationRecipientItem,
        )

        return self.properties.get(
            "additionalNotificationRecipients",
            ClientValueCollection[AccessReviewNotificationRecipientItem](AccessReviewNotificationRecipientItem),
        )

    @property
    def fallback_reviewers(self) -> ClientValueCollection[AccessReviewReviewerScope]:
        """Gets the fallbackReviewers property"""
        from office365.directory.identitygovernance.accessreview.reviewer_scope import (
            AccessReviewReviewerScope,
        )

        return self.properties.get(
            "fallbackReviewers", ClientValueCollection[AccessReviewReviewerScope](AccessReviewReviewerScope)
        )

    @property
    def reviewers(self) -> ClientValueCollection[AccessReviewReviewerScope]:
        """Gets the reviewers property"""
        from office365.directory.identitygovernance.accessreview.reviewer_scope import (
            AccessReviewReviewerScope,
        )

        return self.properties.get(
            "reviewers", ClientValueCollection[AccessReviewReviewerScope](AccessReviewReviewerScope)
        )

    @property
    def stage_settings(self) -> ClientValueCollection[AccessReviewStageSettings]:
        """Gets the stageSettings property"""
        from office365.directory.identitygovernance.accessreview.stage_settings import (
            AccessReviewStageSettings,
        )

        return self.properties.get(
            "stageSettings", ClientValueCollection[AccessReviewStageSettings](AccessReviewStageSettings)
        )
