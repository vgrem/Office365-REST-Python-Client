from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.contentcenter.machinelearning.publicationresult import (
        SPMachineLearningPublicationResult,
    )


class SPMachineLearningPublicationsResult(Entity):
    @property
    def details(self) -> ClientValueCollection[SPMachineLearningPublicationResult]:
        """Gets the Details property"""
        from office365.sharepoint.contentcenter.machinelearning.publicationresult import (
            SPMachineLearningPublicationResult,
        )

        return self.properties.get(
            "Details", ClientValueCollection[SPMachineLearningPublicationResult](SPMachineLearningPublicationResult)
        )

    @property
    def total_failures(self) -> Optional[int]:
        """Gets the TotalFailures property"""
        return self.properties.get("TotalFailures", None)

    @property
    def total_successes(self) -> Optional[int]:
        """Gets the TotalSuccesses property"""
        return self.properties.get("TotalSuccesses", None)

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Office.Server.ContentCenter.SPMachineLearningPublicationsResult"
