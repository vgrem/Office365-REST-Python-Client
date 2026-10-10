from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class ModernizeHomepageResult(Entity):
    """"""

    @property
    def can_modernize_homepage(self) -> Optional[bool]:
        """"""
        return self.properties.get("CanModernizeHomepage", None)

    @property
    def reason(self) -> Optional[str]:
        """Gets the Reason property"""
        return self.properties.get("Reason", None)
