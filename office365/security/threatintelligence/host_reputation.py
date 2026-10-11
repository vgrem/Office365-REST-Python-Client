from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.security.threatintelligence.host_reputation_classification import (
        HostReputationClassification,
    )
    from office365.security.threatintelligence.host_reputation_rule import (
        HostReputationRule,
    )


class HostReputation(Entity):
    @property
    def score(self) -> Optional[int]:
        """Gets the score property"""
        return self.properties.get("score", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.HostReputation"

    @property
    def classification(self) -> HostReputationClassification:
        """Gets the classification property"""
        from office365.security.threatintelligence.host_reputation_classification import (
            HostReputationClassification,
        )

        return self.properties.get("classification", HostReputationClassification.unknown)

    @property
    def rules(self) -> ClientValueCollection[HostReputationRule]:
        """Gets the rules property"""
        from office365.security.threatintelligence.host_reputation_rule import (
            HostReputationRule,
        )

        return self.properties.get("rules", ClientValueCollection[HostReputationRule](HostReputationRule))
