from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.teams.channels.iIdentity import ChannelIdentity
from office365.teams.chats.event_message_detail import EventMessageDetail
from office365.teams.chats.messages.attachment import ChatMessageAttachment
from office365.teams.chats.messages.body import ChatMessageBody
from office365.teams.chats.messages.hosted_content import ChatMessageHostedContent
from office365.teams.chats.messages.mention import ChatMessageMention
from office365.teams.chats.messages.reaction import ChatMessageReaction

if TYPE_CHECKING:
    from office365.teams.chats.messages.history_item import ChatMessageHistoryItem
    from office365.teams.chats.messages.policy_violation import (
        ChatMessagePolicyViolation,
    )


class ChatMessage(Entity):
    """
    Represents an individual chat message within a channel or chat.
    The message can be a root message or part of a thread that is defined by the replyToId property in the message.
    """

    @property
    def attachments(self) -> ClientValueCollection[ChatMessageAttachment]:
        """The collection of replies."""
        return self.properties.get("attachments", ClientValueCollection(ChatMessageAttachment))

    @property
    def body(self) -> ChatMessageBody:
        """
        Plaintext/HTML representation of the content of the chat message. Representation is specified by the
        contentType inside the body. The content is always in HTML if the chat message contains a chatMessageMention.
        """
        return self.properties.get("body", ChatMessageBody())

    @odata(name="channelIdentity")
    @property
    def channel_identity(self) -> ChannelIdentity:
        """
        If the message was sent in a channel, represents identity of the channel.
        """
        return self.properties.get("channelIdentity", ChannelIdentity())

    @property
    def chat_id(self) -> Optional[str]:
        """
        If the message was sent in a chat, represents the identity of the chat.
        """
        return self.properties.get("chatId", None)

    @odata(name="createdDateTime")
    @property
    def created_datetime(self) -> datetime:
        """Timestamp of when the chat message was created."""
        return self.properties.get("createdDateTime", datetime.min)

    @odata(name="lastModifiedDateTime")
    @property
    def last_modified_datetime(self) -> datetime:
        """Timestamp of when the chat message was last modified."""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def etag(self) -> Optional[str]:
        """Version marker for the chat message."""
        return self.properties.get("etag", None)

    @odata(name="from")
    @property
    def from_(self) -> IdentitySet:
        """Details of the sender of the chat message."""
        return self.properties.get("from", IdentitySet())

    @property
    def reply_to_id(self) -> Optional[str]:
        """Id of the parent/root message when this message is a reply."""
        return self.properties.get("replyToId", None)

    @property
    def message_type(self) -> Optional[str]:
        """The type of the chat message (``message``, ``systemEventMessage``, ...)."""
        return self.properties.get("messageType", None)

    @property
    def mentions(self) -> ClientValueCollection[ChatMessageMention]:
        """The mentions for the chat message."""
        return self.properties.get("mentions", ClientValueCollection(ChatMessageMention))

    @property
    def reactions(self) -> ClientValueCollection[ChatMessageReaction]:
        """The reactions for the chat message."""
        return self.properties.get("reactions", ClientValueCollection(ChatMessageReaction))

    @property
    def hosted_contents(self) -> EntityCollection[ChatMessageHostedContent]:
        """Content hosted by Teams as part of the message (e.g. inline images).

        Graph inlines these as plain objects, so normalize the raw list into a
        typed collection for convenient navigation (``id``, ``get_content()``).
        """
        value = self.properties.get("hostedContents")
        if isinstance(value, list):
            collection = EntityCollection(
                self.context, ChatMessageHostedContent, ResourcePath("hostedContents", self.resource_path)
            )
            for index, item in enumerate(value):
                if isinstance(item, dict):
                    collection.set_property(str(index), item, False)
                else:
                    collection.add_child(item)
            return collection
        if value is None:
            return EntityCollection(
                self.context, ChatMessageHostedContent, ResourcePath("hostedContents", self.resource_path)
            )
        return value

    @odata(name="deletedDateTime")
    @property
    def deleted_datetime(self) -> datetime:
        """Read only. Timestamp at which the chat message was deleted, or null if not deleted."""
        return self.properties.get("deletedDateTime", datetime.min)

    @odata(name="eventDetail")
    @property
    def event_detail(self) -> EventMessageDetail:
        """If present, represents details of an event that happened in a chat, a channel, or a team,
        for example, adding new members. For event messages, the messageType property will be set to systemEventMessage.
        """
        return self.properties.get("eventDetail", EventMessageDetail())

    @property
    def replies(self) -> EntityCollection[ChatMessage]:
        """
        The collection of replies.
        """
        return self.properties.get(
            "replies",
            EntityCollection(self.context, ChatMessage, ResourcePath("replies", self.resource_path)),
        )

    @property
    def subject(self) -> Optional[str]:
        """
        The subject of the chat message, in plaintext.
        """
        return self.properties.get("subject", None)

    @property
    def summary(self) -> Optional[str]:
        """
        Summary text of the chat message that could be used for push notifications and summary views or
        fall back views. Only applies to channel chat messages, not chat messages in a chat.
        """
        return self.properties.get("summary", None)

    @property
    def web_url(self) -> Optional[str]:
        """
        Link to the message in Microsoft Teams.
        """
        return self.properties.get("webUrl", None)

    @property
    def importance(self) -> Optional[str]:
        """
        The importance of the chat message. The possible values are: normal, high, urgent.
        """
        return self.properties.get("importance", None)

    @property
    def last_edited_date_time(self) -> Optional[datetime]:
        """Gets the lastEditedDateTime property"""
        return self.properties.get("lastEditedDateTime", datetime.min)

    @property
    def locale(self) -> Optional[str]:
        """Gets the locale property"""
        return self.properties.get("locale", None)

    @property
    def message_history(self) -> ClientValueCollection[ChatMessageHistoryItem]:
        """Gets the messageHistory property"""
        from office365.teams.chats.messages.history_item import ChatMessageHistoryItem

        return self.properties.get(
            "messageHistory", ClientValueCollection[ChatMessageHistoryItem](ChatMessageHistoryItem)
        )

    @property
    def policy_violation(self) -> ChatMessagePolicyViolation:
        """Gets the policyViolation property"""
        from office365.teams.chats.messages.policy_violation import (
            ChatMessagePolicyViolation,
        )

        return self.properties.get("policyViolation", ChatMessagePolicyViolation())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ChatMessage"
