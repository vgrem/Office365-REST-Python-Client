from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class VersionPolicyManager(Entity):
    """ """

    @property
    def default_expire_after_days(self) -> Optional[int]:
        """Gets the DefaultExpireAfterDays property"""
        return self.properties.get("DefaultExpireAfterDays", None)

    @property
    def default_trim_mode(self) -> Optional[int]:
        """Gets the DefaultTrimMode property"""
        return self.properties.get("DefaultTrimMode", None)
