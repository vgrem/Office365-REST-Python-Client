from __future__ import annotations

from typing import Optional

from office365.backuprestore.protection_unit_base import ProtectionUnitBase


class DriveProtectionUnit(ProtectionUnitBase):
    @property
    def directory_object_id(self) -> Optional[str]:
        """Gets the directoryObjectId property"""
        return self.properties.get("directoryObjectId", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def email(self) -> Optional[str]:
        """Gets the email property"""
        return self.properties.get("email", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DriveProtectionUnit"
