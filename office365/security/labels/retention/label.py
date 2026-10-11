from datetime import datetime
from typing import Optional

from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.security.labels.retention.actionafterretentionperiod import (
    ActionAfterRetentionPeriod,
)
from office365.security.labels.retention.behaviorduringretentionperiod import (
    BehaviorDuringRetentionPeriod,
)
from office365.security.labels.retention.defaultrecordbehavior import (
    DefaultRecordBehavior,
)
from office365.security.labels.retention.disposition_review_stage import (
    DispositionReviewStage,
)
from office365.security.labels.retention.duration import RetentionDuration
from office365.security.labels.retention.fileplan_descriptor import (
    FilePlanDescriptor,
)
from office365.security.labels.retention.trigger import RetentionTrigger
from office365.security.triggertypes.event_type import RetentionEventType


class RetentionLabel(Entity):
    """
    Represents how organizations, for compliance and governance purposes, can manage their data at an item
    level (email or document), including whether and for how long to retain or delete the item.

     Organizations can use retention labels for different types of content that require different retention settings.
     For example, they can apply a retention label to tax forms and supporting documents to retain them for
     the period required by law.

     Organizations can configure retention labels with the retention periods and actions based on factors such
     as the date last modified or created. They can also start different retention periods by specifying an event
     that can trigger retention when the event occurs.

     For more information on how retention labels work, when to use them, and how Microsoft Purview supports
     retention labels to let you configure retention and deletion settings, see Learn about retention policies and
     retention labels.
    """

    @odata(name="actionAfterRetentionPeriod")
    @property
    def action_after_retention_period(self) -> ActionAfterRetentionPeriod:
        """Specifies the action to take after the retention period expires."""
        return self.properties.get("actionAfterRetentionPeriod", ActionAfterRetentionPeriod.none)

    @odata(name="behaviorDuringRetentionPeriod")
    @property
    def behavior_during_retention_period(self) -> BehaviorDuringRetentionPeriod:
        """Specifies how the behavior of a document with this label should be during the retention period."""
        return self.properties.get("behaviorDuringRetentionPeriod", BehaviorDuringRetentionPeriod.none)

    @odata(name="createdBy")
    @property
    def created_by(self) -> IdentitySet:
        """Represents the user who created the retentionLabel."""
        return self.properties.get("createdBy", IdentitySet())

    @odata(name="createdDateTime")
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Date and time the retention label was created."""
        return self.properties.get("createdDateTime", None)

    @odata(name="defaultRecordBehavior")
    @property
    def default_record_behavior(self) -> DefaultRecordBehavior:
        """Specifies the default record behavior for the label."""
        return self.properties.get("defaultRecordBehavior", DefaultRecordBehavior.startLocked)

    @odata(name="descriptionForAdmins")
    @property
    def description_for_admins(self) -> Optional[str]:
        """Provides the label information for the admin. Optional."""
        return self.properties.get("descriptionForAdmins", None)

    @property
    def description_for_users(self) -> Optional[str]:
        """Provides the label information for the user. Optional."""
        return self.properties.get("descriptionForUsers", None)

    @property
    def display_name(self) -> Optional[str]:
        """Display name of the retention label."""
        return self.properties.get("displayName", None)

    @property
    def is_in_use(self) -> Optional[bool]:
        """Indicates whether the label is currently in use."""
        return self.properties.get("isInUse", None)

    @property
    def label_to_be_applied(self) -> Optional[str]:
        """Specifies the replacement label to apply when the original label is removed."""
        return self.properties.get("labelToBeApplied", None)

    @odata(name="lastModifiedBy")
    @property
    def last_modified_by(self) -> IdentitySet:
        """Represents the user who last modified the retentionLabel."""
        return self.properties.get("lastModifiedBy", IdentitySet())

    @odata(name="lastModifiedDateTime")
    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Date and time the retention label was last modified."""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @odata(name="retentionDuration")
    @property
    def retention_duration(self) -> RetentionDuration:
        """Specifies the number of days to retain the content."""
        return self.properties.get("retentionDuration", RetentionDuration())

    @odata(name="retentionTrigger")
    @property
    def retention_trigger(self) -> RetentionTrigger:
        """Specifies whether the retention duration is calculated from the content creation date, labeled date,
        or last modification date."""
        return self.properties.get("retentionTrigger", RetentionTrigger.none)

    @property
    def descriptors(self) -> FilePlanDescriptor:
        """Represents a file plan descriptor for the retention label."""
        return self.properties.get(
            "descriptors",
            FilePlanDescriptor(self.context, ResourcePath("descriptors", self.resource_path)),
        )

    @odata(name="dispositionReviewStages")
    @property
    def disposition_review_stages(self) -> EntityCollection[DispositionReviewStage]:
        """Represents disposition review stages for the retention label."""
        return self.properties.get(
            "dispositionReviewStages",
            EntityCollection(
                self.context, DispositionReviewStage, ResourcePath("dispositionReviewStages", self.resource_path)
            ),
        )

    @odata(name="retentionEventType")
    @property
    def retention_event_type(self) -> RetentionEventType:
        """Specifies the retention event type for the label."""
        return self.properties.get(
            "retentionEventType",
            RetentionEventType(self.context, ResourcePath("retentionEventType", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return None  # type: ignore
