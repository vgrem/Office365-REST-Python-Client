from __future__ import annotations

from typing import Optional

from office365.entity import Entity
from office365.security.healthissues.sourcetype import SourceType


class UserSource(Entity):
    @property
    def email(self) -> Optional[str]:
        """Gets the email property"""
        return self.properties.get("email", None)

    @property
    def included_sources(self) -> SourceType:
        """Gets the includedSources property"""
        return self.properties.get("includedSources", SourceType.mailbox)

    @property
    def site_web_url(self) -> Optional[str]:
        """Gets the siteWebUrl property"""
        return self.properties.get("siteWebUrl", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.UserSource"
