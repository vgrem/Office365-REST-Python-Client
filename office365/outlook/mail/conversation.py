from datetime import datetime
from typing import Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.mail.conversation_thread import ConversationThread
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata


class Conversation(Entity):
    """
    A conversation is a collection of threads, and a thread contains posts to that thread.
    All threads and posts in a conversation share the same subject.
    """

    @odata(name="hasAttachments")
    @property
    def has_attachments(self) -> Optional[bool]:
        """
        Indicates whether any of the posts within this Conversation has at least one attachment.
        Supports $filter (eq, ne) and $search.
        """
        return self.properties.get("hasAttachments", None)

    @odata(name="lastDeliveredDateTime")
    @property
    def last_delivered_datetime(self) -> datetime:
        """The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time."""
        return self.properties.get("lastDeliveredDateTime", datetime.min)

    @odata(name="preview")
    @property
    def preview(self) -> Optional[str]:
        """
        A short summary from the body of the latest post in this conversation.
        Supports $filter (eq, ne, le, ge).
        """
        return self.properties.get("preview", None)

    @odata(name="topic")
    @property
    def topic(self) -> Optional[str]:
        """
        The topic of the conversation. This property can be set when the conversation is created, but it cannot be
        updated.
        """
        return self.properties.get("topic", None)

    @odata(name="uniqueSenders")
    @property
    def unique_senders(self) -> StringCollection:
        """All the users that sent a message to this Conversation."""
        return self.properties.get("uniqueSenders", StringCollection())

    @odata(name="threads", navigation=True)
    @property
    def threads(self) -> EntityCollection[ConversationThread]:
        """A collection of all the conversation threads in the conversation."""
        return self.properties.get(
            "threads", EntityCollection(self.context, ConversationThread, ResourcePath("threads", self.resource_path))
        )

    @odata(name="lastDeliveredDateTime")
    @property
    def last_delivered_date_time(self) -> datetime:
        """Gets the lastDeliveredDateTime property"""
        return self.properties.get("lastDeliveredDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Conversation"
