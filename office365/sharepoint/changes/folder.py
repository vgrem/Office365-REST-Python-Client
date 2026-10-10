from __future__ import annotations

from typing import Optional

from office365.sharepoint.changes.change import Change


class ChangeFolder(Change):
    """Specifies a change on a folder not contained in a list or document library."""

    @property
    def unique_id(self) -> Optional[str]:
        """Identifies the folder that has changed."""
        return self.properties.get("UniqueId", None)

    @property
    def web_id(self) -> Optional[str]:
        """Identifies the site that contains the changed folder."""
        return self.properties.get("WebId", None)

    @property
    def is_recycle_bin_operation(self) -> Optional[bool]:
        """Gets the IsRecycleBinOperation property"""
        return self.properties.get("IsRecycleBinOperation", None)
