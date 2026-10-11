from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.security.intelligence_profile_indicator import (
    IntelligenceProfileIndicator,
)

if TYPE_CHECKING:
    from office365.security.formatted_content import FormattedContent
    from office365.security.intelligence_profile_country_or_region_of_origin import (
        IntelligenceProfileCountryOrRegionOfOrigin,
    )
    from office365.security.intelligence_profile_kind import (
        IntelligenceProfileKind,
    )


class IntelligenceProfile(Entity):
    """
    The Microsoft Defender Threat Intelligence Profiles (Intel Profiles) API provides the most up-to-date threat actor
    infrastructure visibility in the industry today, enabling threat intelligence and security operations (SecOps)
    teams to streamline their advanced threat hunting and analysis workflows. These teams have historically
    struggled to obtain visibility into the full extent of nation state and cybercriminal adversary infrastructures,
    creating blind spots in detection and response automation, hunting, and analytics. Sophisticated security
    professionals can use Microsoft Intelligence Profile APIs, along with the indicators and other associated markers,
    to automate defense of their organizations and track potentially malicious activity targeting their organization
    or industry. Users of the Microsoft Defender Threat Intelligence Profiles APIs have access to detailed threat
    actor intel profiles, including background information and interpretation guidance.
    """

    @property
    def aliases(self) -> StringCollection:
        """Gets the aliases property"""
        return self.properties.get("aliases", StringCollection(None))

    @property
    def first_active_date_time(self) -> datetime:
        """Gets the firstActiveDateTime property"""
        return self.properties.get("firstActiveDateTime", datetime.min)

    @property
    def targets(self) -> StringCollection:
        """Gets the targets property"""
        return self.properties.get("targets", StringCollection(None))

    @property
    def title(self) -> Optional[str]:
        """Gets the title property"""
        return self.properties.get("title", None)

    @property
    def indicators(self) -> EntityCollection[IntelligenceProfileIndicator]:
        """Gets the indicators property"""
        return self.properties.get(
            "indicators",
            EntityCollection[IntelligenceProfileIndicator](
                self.context, IntelligenceProfileIndicator, ResourcePath("indicators", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.IntelligenceProfile"

    @property
    def countries_or_regions_of_origin(self) -> ClientValueCollection[IntelligenceProfileCountryOrRegionOfOrigin]:
        """Gets the countriesOrRegionsOfOrigin property"""
        from office365.security.intelligence_profile_country_or_region_of_origin import (
            IntelligenceProfileCountryOrRegionOfOrigin,
        )

        return self.properties.get(
            "countriesOrRegionsOfOrigin",
            ClientValueCollection[IntelligenceProfileCountryOrRegionOfOrigin](
                IntelligenceProfileCountryOrRegionOfOrigin
            ),
        )

    @property
    def description(self) -> FormattedContent:
        """Gets the description property"""
        from office365.security.formatted_content import FormattedContent

        return self.properties.get("description", FormattedContent())

    @property
    def kind(self) -> IntelligenceProfileKind:
        """Gets the kind property"""
        from office365.security.intelligence_profile_kind import (
            IntelligenceProfileKind,
        )

        return self.properties.get("kind", IntelligenceProfileKind.actor)

    @property
    def summary(self) -> FormattedContent:
        """Gets the summary property"""
        from office365.security.formatted_content import FormattedContent

        return self.properties.get("summary", FormattedContent())

    @property
    def tradecraft(self) -> FormattedContent:
        """Gets the tradecraft property"""
        from office365.security.formatted_content import FormattedContent

        return self.properties.get("tradecraft", FormattedContent())
