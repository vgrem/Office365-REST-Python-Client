from typing import Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class DispositionReviewStage(Entity):
    """Represents a disposition review stage for a retention label."""

    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def reviewers_email_addresses(self) -> StringCollection:
        """Gets the reviewersEmailAddresses property"""
        return self.properties.get("reviewersEmailAddresses", StringCollection(None))

    @property
    def stage_number(self) -> Optional[str]:
        """Gets the stageNumber property"""
        return self.properties.get("stageNumber", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.DispositionReviewStage"
