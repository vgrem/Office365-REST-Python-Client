from datetime import datetime
from typing import Optional

from typing_extensions import Self

from office365.directory.permissions.require_permission import require_permission
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.mail.post import Post
from office365.outlook.mail.recipient import Recipient
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata


class ConversationThread(Entity):
    """A conversationThread is a collection of posts."""

    @require_permission(delegated=["Group.ReadWrite.All"], application=["Group.ReadWrite.All"])
    def reply(self, post: Post) -> Self:
        """Reply to a thread in a group conversation and add a new post to it. You can specify the parent conversation
        in the request, or, you can specify just the thread without the parent conversation.

        Args:
            post (Post): A comment to include. Can be an empty string.
        """
        payload = {"post": post}
        qry = ServiceOperationQuery(self, "reply", None, payload)
        self.context.add_query(qry)
        return self

    @odata(name="ccRecipients")
    @property
    def cc_recipients(self) -> ClientValueCollection[Recipient]:
        """The Cc: recipients for the thread."""
        return self.properties.get("ccRecipients", ClientValueCollection(Recipient))

    @odata(name="hasAttachments")
    @property
    def has_attachments(self) -> Optional[bool]:
        """Indicates whether any of the posts within this thread has at least one attachment."""
        return self.properties.get("hasAttachments", None)

    @odata(name="toRecipients")
    @property
    def to_recipients(self) -> ClientValueCollection[Recipient]:
        """The To: recipients for the thread."""
        return self.properties.get("toRecipients", ClientValueCollection(Recipient))

    @odata(name="posts", navigation=True)
    @property
    def posts(self) -> EntityCollection[Post]:
        """"""
        return self.properties.get(
            "posts", EntityCollection(self.context, Post, ResourcePath("posts", self.resource_path))
        )

    @odata(name="isLocked")
    @property
    def is_locked(self) -> Optional[bool]:
        """Gets the isLocked property"""
        return self.properties.get("isLocked", None)

    @odata(name="lastDeliveredDateTime")
    @property
    def last_delivered_date_time(self) -> datetime:
        """Gets the lastDeliveredDateTime property"""
        return self.properties.get("lastDeliveredDateTime", datetime.min)

    @odata(name="preview")
    @property
    def preview(self) -> Optional[str]:
        """Gets the preview property"""
        return self.properties.get("preview", None)

    @odata(name="topic")
    @property
    def topic(self) -> Optional[str]:
        """Gets the topic property"""
        return self.properties.get("topic", None)

    @odata(name="uniqueSenders")
    @property
    def unique_senders(self) -> StringCollection:
        """Gets the uniqueSenders property"""
        return self.properties.get("uniqueSenders", StringCollection(None))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ConversationThread"
