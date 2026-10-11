from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue
from office365.security.labels.retention.behaviorduringretentionperiod import BehaviorDuringRetentionPeriod


@dataclass
class RetentionLabelSettings(ClientValue):
    """
    Groups all the compliance retention restrictions on the item into a single structure.
    """

    behaviorDuringRetentionPeriod: BehaviorDuringRetentionPeriod | None = None
    isContentUpdateAllowed: bool | None = None
    isDeleteAllowed: bool | None = None
    isLabelUpdateAllowed: bool | None = None
    isMetadataUpdateAllowed: bool | None = None
    isRecordLocked: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RetentionLabelSettings"
