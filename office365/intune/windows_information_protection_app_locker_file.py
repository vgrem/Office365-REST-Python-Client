from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class WindowsInformationProtectionAppLockerFile(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def file(self) -> Optional[bytes]:
        """Gets the file property"""
        return self.properties.get("file", None)

    @property
    def file_hash(self) -> Optional[str]:
        """Gets the fileHash property"""
        return self.properties.get("fileHash", None)

    @property
    def version(self) -> Optional[str]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsInformationProtectionAppLockerFile"
