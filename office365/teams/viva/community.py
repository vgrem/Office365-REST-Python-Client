from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.groups.group import Group
    from office365.directory.users.user import User
    from office365.teams.community_privacy import CommunityPrivacy


class Community(Entity):
    """Represents a community in Viva Engage that is a central place for conversations, files, events, and
     updates for people sharing a common interest or goal.

    Every community is associated with a Microsoft 365 group, but the group doesn't have the same ID as the community.
    For more information about managing communities in Viva Engage, see Use the Microsoft Graph API to work
    with Viva Engage.

    This resource is an open type that allows other properties to be passed in.
    """

    def __str__(self):
        return self.display_name or self.entity_type_name

    @property
    def display_name(self) -> Optional[str]:
        """The name of the community. The maximum length is 255 characters."""
        return self.properties.get("displayName", None)

    @property
    def description(self) -> Optional[str]:
        """The description of the community. The maximum length is 1,024 characters."""
        return self.properties.get("description", None)

    @property
    def group_id(self) -> Optional[str]:
        """Gets the groupId property"""
        return self.properties.get("groupId", None)

    @property
    def privacy(self) -> CommunityPrivacy:
        """Gets the privacy property"""
        from office365.teams.community_privacy import CommunityPrivacy

        return self.properties.get("privacy", CommunityPrivacy.public)

    @property
    def group(self) -> Group:
        """Gets the group property"""
        from office365.directory.groups.group import Group

        return self.properties.get("group", Group(self.context, ResourcePath("group", self.resource_path)))

    @property
    def owners(self) -> EntityCollection[User]:
        """Gets the owners property"""
        from office365.directory.users.user import User

        return self.properties.get(
            "owners", EntityCollection[User](self.context, User, ResourcePath("owners", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Community"
