from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from office365.directory.permissions.grants.resource_specific import (
    ResourceSpecificPermissionGrant,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.teams.apps.installation import TeamsAppInstallation
from office365.teams.chats.messages.collection import ChatMessageCollection
from office365.teams.chats.messages.info import ChatMessageInfo
from office365.teams.chats.viewpoint import ChatViewpoint
from office365.teams.members.conversation_collection import ConversationMemberCollection
from office365.teams.operations.async_operation import TeamsAsyncOperation
from office365.teams.tabs.tab import TeamsTab
from office365.teams.teamwork.online_meeting_info import TeamworkOnlineMeetingInfo

if TYPE_CHECKING:
    from office365.teams.chats.pinned_chat_message_info import PinnedChatMessageInfo
    from office365.teams.chats.targeted_chat_message import TargetedChatMessage
    from office365.teams.migration_mode import MigrationMode


class Chat(Entity):
    """A chat is a collection of chatMessages between one or more participants. Participants can be users or apps."""

    @property
    def chat_type(self) -> str | None:
        """Specifies the type of chat. Possible values are: group, oneOnOne, meeting, unknownFutureValue."""
        return self.properties.get("chatType", None)

    @odata(name="createdDateTime")
    @property
    def created_datetime(self) -> datetime:
        """Date and time at which the chat was created."""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def is_hidden_for_all_members(self) -> bool | None:
        """Indicates whether the chat is hidden for all its members."""
        return self.properties.get("isHiddenForAllMembers", None)

    @odata(name="lastUpdatedDateTime")
    @property
    def last_updated_datetime(self) -> datetime | None:
        """Date and time at which the chat was renamed or the list of members was last changed."""
        return self.properties.get("lastUpdatedDateTime", datetime.min)

    @odata(name="onlineMeetingInfo")
    @property
    def online_meeting_info(self) -> TeamworkOnlineMeetingInfo:
        """Represents details about an online meeting. If the chat isn't associated with an online meeting,
        the property is empty. Read-only."""
        return self.properties.get("onlineMeetingInfo", TeamworkOnlineMeetingInfo())

    @property
    def tenant_id(self) -> str | None:
        """The identifier of the tenant in which the chat was created. Read-only."""
        return self.properties.get("tenantId", None)

    @property
    def topic(self) -> str | None:
        """(Optional) Subject or topic for the chat. Only available for group chats."""
        return self.properties.get("topic", None)

    @property
    def viewpoint(self) -> ChatViewpoint:
        """Represents caller-specific information about the chat, such as the last message read date and time.
        This property is populated only when the request is made in a delegated context.
        """
        return self.properties.get("viewpoint", ChatViewpoint())

    @property
    def web_url(self) -> str | None:
        """The URL for the chat in Microsoft Teams. The URL should be treated as an opaque blob, and not parsed."""
        return self.properties.get("webUrl", None)

    @odata(name="installedApps")
    @property
    def installed_apps(self) -> EntityCollection[TeamsAppInstallation]:
        """A collection of all the apps in the chat. Nullable."""
        return self.properties.get(
            "installedApps",
            EntityCollection(self.context, TeamsAppInstallation, ResourcePath("installedApps", self.resource_path)),
        )

    @odata(name="lastMessagePreview")
    @property
    def last_message_preview(self) -> ChatMessageInfo:
        """Preview of the last message sent in the chat. Null if no messages have been sent in the chat."""
        return self.properties.get(
            "lastMessagePreview", ChatMessageInfo(self.context, ResourcePath("lastMessagePreview", self.resource_path))
        )

    @odata(name="members", persist=True)
    @property
    def members(self) -> ConversationMemberCollection:
        """A collection of membership records associated with the chat."""
        return self.properties.setdefault(
            "members", ConversationMemberCollection(self.context, ResourcePath("members", self.resource_path))
        )

    @property
    def messages(self) -> ChatMessageCollection:
        """A collection of all the messages in the chat. Nullable."""
        return self.properties.get(
            "messages", ChatMessageCollection(self.context, ResourcePath("messages", self.resource_path))
        )

    @property
    def operations(self) -> EntityCollection[TeamsAsyncOperation]:
        """
        A collection of all the Teams async operations that ran or are running on the chat. Nullable.
        """
        return self.properties.get(
            "operations",
            EntityCollection(self.context, TeamsAsyncOperation, ResourcePath("operations", self.resource_path)),
        )

    @property
    def tabs(self) -> EntityCollection[TeamsTab]:
        """A collection of all the tabs in the chat."""
        return self.properties.get(
            "tabs", EntityCollection(self.context, TeamsTab, ResourcePath("tabs", self.resource_path))
        )

    @property
    def original_created_date_time(self) -> datetime | None:
        """Gets the originalCreatedDateTime property"""
        return self.properties.get("originalCreatedDateTime", datetime.min)

    @property
    def permission_grants(self) -> EntityCollection[ResourceSpecificPermissionGrant]:
        """Gets the permissionGrants property"""
        return self.properties.get(
            "permissionGrants",
            EntityCollection[ResourceSpecificPermissionGrant](
                self.context, ResourceSpecificPermissionGrant, ResourcePath("permissionGrants", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Chat"

    @property
    def migration_mode(self) -> MigrationMode:
        """Gets the migrationMode property"""
        from office365.teams.migration_mode import MigrationMode

        return self.properties.get("migrationMode", MigrationMode.inProgress)

    @property
    def pinned_messages(self) -> EntityCollection[PinnedChatMessageInfo]:
        """Gets the pinnedMessages property"""
        from office365.teams.chats.pinned_chat_message_info import PinnedChatMessageInfo

        return self.properties.get(
            "pinnedMessages",
            EntityCollection[PinnedChatMessageInfo](
                self.context, PinnedChatMessageInfo, ResourcePath("pinnedMessages", self.resource_path)
            ),
        )

    @property
    def targeted_messages(self) -> EntityCollection[TargetedChatMessage]:
        """Gets the targetedMessages property"""
        from office365.teams.chats.targeted_chat_message import TargetedChatMessage

        return self.properties.get(
            "targetedMessages",
            EntityCollection[TargetedChatMessage](
                self.context, TargetedChatMessage, ResourcePath("targetedMessages", self.resource_path)
            ),
        )
