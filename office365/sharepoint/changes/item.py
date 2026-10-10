from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.odata_property import odata
from office365.sharepoint.changes.change import Change
from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from office365.sharepoint.sharing.shared_with_user import SharedWithUser


class ChangeItem(Change):
    """A change on an item."""

    @property
    def activity_type(self) -> Optional[str]:
        """Returns activity type defined in ChangeActivityType"""
        return self.properties.get("ActivityType", None)

    @odata(name="ContentTypeId")
    @property
    def content_type_id(self):
        """Specifies an identifier for the content type"""
        return self.properties.get("ContentTypeId", ContentTypeId())

    @property
    def editor(self):
        """Specifies the editor of the changed item."""
        return self.properties.get("Editor", None)

    @property
    def editor_email_hint(self):
        """Returns the email corresponding to Editor."""
        return self.properties.get("EditorEmailHint", None)

    @property
    def editor_login_name(self):
        """Returns login name of the Editor."""
        return self.properties.get("EditorLoginName", None)

    @property
    def file_type(self) -> Optional[str]:
        """Returns the list item’s file type."""
        return self.properties.get("FileType", None)

    @property
    def item_id(self) -> Optional[int]:
        """Identifies the changed item."""
        return self.properties.get("ItemId", None)

    @property
    def is_recycle_bin_operation(self) -> Optional[bool]:
        return self.properties.get("IsRecycleBinOperation", None)

    @property
    def server_relative_url(self) -> Optional[str]:
        """Specifies the server-relative URL of the item."""
        return self.properties.get("ServerRelativeUrl", None)

    @odata(name="SharedByUser")
    @property
    def shared_by_user(self):
        """Return the sharedBy User Information in sharing action for change log."""
        return self.properties.get("SharedByUser", SharedWithUser())

    @odata(name="SharedWithUsers")
    @property
    def shared_with_users(self):
        """Returns the array of users that have been shared in sharing action for the change log."""
        return self.properties.get("SharedWithUsers", ClientValueCollection(SharedWithUser))

    @property
    def unique_id(self) -> Optional[str]:
        """The Document identifier of the item."""
        return self.properties.get("UniqueId", None)

    @property
    def file_system_object_type(self) -> Optional[int]:
        """Gets the FileSystemObjectType property"""
        return self.properties.get("FileSystemObjectType", None)

    @property
    def hashtag(self) -> Optional[str]:
        """Gets the Hashtag property"""
        return self.properties.get("Hashtag", None)

    @property
    def hidden(self) -> Optional[bool]:
        """Gets the Hidden property"""
        return self.properties.get("Hidden", None)

    @property
    def list_id(self) -> Optional[UUID]:
        """Gets the ListId property"""
        return self.properties.get("ListId", None)

    @property
    def list_template(self) -> Optional[int]:
        """Gets the ListTemplate property"""
        return self.properties.get("ListTemplate", None)

    @property
    def list_title(self) -> Optional[str]:
        """Gets the ListTitle property"""
        return self.properties.get("ListTitle", None)

    @property
    def move_was_for_recycle(self) -> Optional[bool]:
        """Gets the MoveWasForRecycle property"""
        return self.properties.get("MoveWasForRecycle", None)

    @property
    def move_was_for_restore(self) -> Optional[bool]:
        """Gets the MoveWasForRestore property"""
        return self.properties.get("MoveWasForRestore", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def web_id(self) -> Optional[UUID]:
        """Gets the WebId property"""
        return self.properties.get("WebId", None)
