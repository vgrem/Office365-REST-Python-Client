from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class CitationTemplate(Entity):
    @property
    def citation_jurisdiction(self) -> Optional[str]:
        """Gets the citationJurisdiction property"""
        return self.properties.get("citationJurisdiction", None)

    @property
    def citation_url(self) -> Optional[str]:
        """Gets the citationUrl property"""
        return self.properties.get("citationUrl", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.CitationTemplate"
