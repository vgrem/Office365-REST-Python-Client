from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class FileHandlerWopiProperties(Entity):
    """"""

    @property
    def entity_type_name(self):
        return "SP.Utilities.FileHandlerWopiProperties"

    @property
    def file_get_url(self) -> Optional[str]:
        """Gets the FileGetUrl property"""
        return self.properties.get("FileGetUrl", None)

    @property
    def file_id(self) -> Optional[str]:
        """Gets the FileId property"""
        return self.properties.get("FileId", None)

    @property
    def file_put_url(self) -> Optional[str]:
        """Gets the FilePutUrl property"""
        return self.properties.get("FilePutUrl", None)

    @property
    def resource_id(self) -> Optional[str]:
        """Gets the ResourceId property"""
        return self.properties.get("ResourceId", None)
