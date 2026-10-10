from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class MountedFolderInfo(Entity):
    """"""

    @property
    def folder_url(self) -> Optional[str]:
        """Gets the FolderUrl property"""
        return self.properties.get("FolderUrl", None)

    @property
    def has_edit_permission(self) -> Optional[bool]:
        """Gets the HasEditPermission property"""
        return self.properties.get("HasEditPermission", None)

    @property
    def item_id(self) -> Optional[int]:
        """Gets the ItemId property"""
        return self.properties.get("ItemId", None)

    @property
    def list_template_type(self) -> Optional[int]:
        """Gets the ListTemplateType property"""
        return self.properties.get("ListTemplateType", None)

    @property
    def list_view_url(self) -> Optional[str]:
        """Gets the ListViewUrl property"""
        return self.properties.get("ListViewUrl", None)

    @property
    def web_url(self) -> Optional[str]:
        """Gets the WebUrl property"""
        return self.properties.get("WebUrl", None)
