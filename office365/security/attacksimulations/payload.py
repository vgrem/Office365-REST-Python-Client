from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.directory.permissions.email_identity import EmailIdentity
    from office365.security.attacksimulations.payloadbrand import PayloadBrand
    from office365.security.attacksimulations.payloadcomplexity import (
        PayloadComplexity,
    )
    from office365.security.attacksimulations.payloaddeliveryplatform import (
        PayloadDeliveryPlatform,
    )
    from office365.security.attacksimulations.payloadindustry import (
        PayloadIndustry,
    )
    from office365.security.attacksimulations.payloadtheme import PayloadTheme
    from office365.security.attacksimulations.simulationattacktechnique import (
        SimulationAttackTechnique,
    )
    from office365.security.attacksimulations.simulationattacktype import (
        SimulationAttackType,
    )
    from office365.security.attacksimulations.simulationcontentsource import (
        SimulationContentSource,
    )
    from office365.security.attacksimulations.simulationcontentstatus import (
        SimulationContentStatus,
    )
    from office365.security.payload_detail import PayloadDetail


class Payload(Entity):
    @property
    def brand(self) -> PayloadBrand:
        """Gets the brand property"""
        from office365.security.attacksimulations.payloadbrand import (
            PayloadBrand,
        )

        return self.properties.get("brand", PayloadBrand.unknown)

    @property
    def complexity(self) -> PayloadComplexity:
        """Gets the complexity property"""
        from office365.security.attacksimulations.payloadcomplexity import (
            PayloadComplexity,
        )

        return self.properties.get("complexity", PayloadComplexity.unknown)

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
    def detail(self) -> PayloadDetail:
        """Gets the detail property"""
        from office365.security.payload_detail import PayloadDetail

        return self.properties.get("detail", PayloadDetail())

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def industry(self) -> PayloadIndustry:
        """Gets the industry property"""
        from office365.security.attacksimulations.payloadindustry import (
            PayloadIndustry,
        )

        return self.properties.get("industry", PayloadIndustry.unknown)

    @property
    def is_automated(self) -> Optional[bool]:
        """Gets the isAutomated property"""
        return self.properties.get("isAutomated", None)

    @property
    def is_controversial(self) -> Optional[bool]:
        """Gets the isControversial property"""
        return self.properties.get("isControversial", None)

    @property
    def is_current_event(self) -> Optional[bool]:
        """Gets the isCurrentEvent property"""
        return self.properties.get("isCurrentEvent", None)

    @property
    def language(self) -> Optional[str]:
        """Gets the language property"""
        return self.properties.get("language", None)

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
    def payload_tags(self) -> StringCollection:
        """Gets the payloadTags property"""
        return self.properties.get("payloadTags", StringCollection())

    @property
    def platform(self) -> PayloadDeliveryPlatform:
        """Gets the platform property"""
        from office365.security.attacksimulations.payloaddeliveryplatform import (
            PayloadDeliveryPlatform,
        )

        return self.properties.get("platform", PayloadDeliveryPlatform.unknown)

    @property
    def predicted_compromise_rate(self) -> Optional[float]:
        """Gets the predictedCompromiseRate property"""
        return self.properties.get("predictedCompromiseRate", None)

    @property
    def simulation_attack_type(self) -> SimulationAttackType:
        """Gets the simulationAttackType property"""
        from office365.security.attacksimulations.simulationattacktype import (
            SimulationAttackType,
        )

        return self.properties.get("simulationAttackType", SimulationAttackType.unknown)

    @property
    def source(self) -> SimulationContentSource:
        """Gets the source property"""
        from office365.security.attacksimulations.simulationcontentsource import (
            SimulationContentSource,
        )

        return self.properties.get("source", SimulationContentSource.unknown)

    @property
    def status(self) -> SimulationContentStatus:
        """Gets the status property"""
        from office365.security.attacksimulations.simulationcontentstatus import (
            SimulationContentStatus,
        )

        return self.properties.get("status", SimulationContentStatus.unknown)

    @property
    def technique(self) -> SimulationAttackTechnique:
        """Gets the technique property"""
        from office365.security.attacksimulations.simulationattacktechnique import (
            SimulationAttackTechnique,
        )

        return self.properties.get("technique", SimulationAttackTechnique.unknown)

    @property
    def theme(self) -> PayloadTheme:
        """Gets the theme property"""
        from office365.security.attacksimulations.payloadtheme import (
            PayloadTheme,
        )

        return self.properties.get("theme", PayloadTheme.unknown)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Payload"
