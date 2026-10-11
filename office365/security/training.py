from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.directory.permissions.email_identity import EmailIdentity
    from office365.security.attacksimulations.simulationcontentsource import (
        SimulationContentSource,
    )
    from office365.security.attacksimulations.trainingavailabilitystatus import (
        TrainingAvailabilityStatus,
    )
    from office365.security.attacksimulations.trainingtype import TrainingType
    from office365.security.training_language_detail import (
        TrainingLanguageDetail,
    )


class Training(Entity):
    @property
    def availability_status(self) -> TrainingAvailabilityStatus:
        """Gets the availabilityStatus property"""
        from office365.security.attacksimulations.trainingavailabilitystatus import (
            TrainingAvailabilityStatus,
        )

        return self.properties.get("availabilityStatus", TrainingAvailabilityStatus.unknown)

    @property
    def created_by(self) -> EmailIdentity:
        """Gets the createdBy property"""
        from office365.directory.permissions.email_identity import EmailIdentity

        return self.properties.get("createdBy", EmailIdentity())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def duration_in_minutes(self) -> Optional[int]:
        """Gets the durationInMinutes property"""
        return self.properties.get("durationInMinutes", None)

    @property
    def has_evaluation(self) -> Optional[bool]:
        """Gets the hasEvaluation property"""
        return self.properties.get("hasEvaluation", None)

    @property
    def last_modified_by(self) -> EmailIdentity:
        """Gets the lastModifiedBy property"""
        from office365.directory.permissions.email_identity import EmailIdentity

        return self.properties.get("lastModifiedBy", EmailIdentity())

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def source(self) -> SimulationContentSource:
        """Gets the source property"""
        from office365.security.attacksimulations.simulationcontentsource import (
            SimulationContentSource,
        )

        return self.properties.get("source", SimulationContentSource.unknown)

    @property
    def supported_locales(self) -> StringCollection:
        """Gets the supportedLocales property"""
        return self.properties.get("supportedLocales", StringCollection())

    @property
    def tags(self) -> StringCollection:
        """Gets the tags property"""
        return self.properties.get("tags", StringCollection())

    @property
    def type(self) -> TrainingType:
        """Gets the type property"""
        from office365.security.attacksimulations.trainingtype import (
            TrainingType,
        )

        return self.properties.get("type", TrainingType.unknown)

    @property
    def language_details(self) -> EntityCollection[TrainingLanguageDetail]:
        """Gets the languageDetails property"""
        from office365.security.training_language_detail import (
            TrainingLanguageDetail,
        )

        return self.properties.get(
            "languageDetails",
            EntityCollection[TrainingLanguageDetail](
                self.context, TrainingLanguageDetail, ResourcePath("languageDetails", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Training"
