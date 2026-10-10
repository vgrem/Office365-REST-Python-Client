from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.changes.change import Change


class ChangeList(Change):
    """
    Specifies a change on a list.

    The RelativeTime and RootFolderUrl properties are not included in the default scalar property set for this type.
    """

    def __repr__(self):
        return f"List: {self.list_id}"

    @property
    def base_template(self) -> Optional[int]:
        """An SP.ListTemplateType object that returns the list template type of the list."""
        return self.properties.get("BaseTemplate", None)

    @property
    def editor(self) -> Optional[str]:
        """A string that returns the name of the user who modified the list."""
        return self.properties.get("Editor", None)

    @property
    def hidden(self) -> Optional[bool]:
        """Returns a Boolean value that indicates whether a list is a hidden list."""
        return self.properties.get("Hidden", None)

    @property
    def list_id(self) -> Optional[str]:
        """Identifies the changed list"""
        return self.properties.get("ListId", None)

    @property
    def creator(self):
        """An SP.User object that represents information about the user who created the list."""
        from office365.sharepoint.principal.users.user import User

        return self.properties.get("Creator", User(self.context, ResourcePath("Creator", self.resource_path)))

    @property
    def is_recycle_bin_operation(self) -> Optional[bool]:
        """Gets the IsRecycleBinOperation property"""
        return self.properties.get("IsRecycleBinOperation", None)

    @property
    def root_folder_url(self) -> Optional[str]:
        """Gets the RootFolderUrl property"""
        return self.properties.get("RootFolderUrl", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def web_id(self) -> Optional[UUID]:
        """Gets the WebId property"""
        return self.properties.get("WebId", None)
