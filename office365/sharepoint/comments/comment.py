from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata
from office365.sharepoint.comments.client.identity import Identity
from office365.sharepoint.comments.contentanchor import ContentAnchor
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.likes.user_entity import UserEntity
from office365.sharepoint.sharing.principal import Principal

if TYPE_CHECKING:
    from office365.sharepoint.comments.comment import Comment


class Comment(Entity):
    def like(self) -> Self:
        """
        The Like method makes the current user a liker of the comment.
        """
        qry = ServiceOperationQuery(self, "Like")
        self.context.add_query(qry)
        return self

    def unlike(self) -> Self:
        """
        The Unlike method removes the current user from the list of likers for the comment.
        """
        qry = ServiceOperationQuery(self, "Unlike")
        self.context.add_query(qry)
        return self

    @odata(name="likedBy")
    @property
    def liked_by(self) -> EntityCollection[UserEntity]:
        """
        List of like entries corresponding to individual likes. MUST NOT contain more than one entry
        for the same user in the set.
        """
        return self.properties.get(
            "likedBy", EntityCollection(self.context, UserEntity, ResourcePath("likedBy", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.Comments.comment"

    @property
    def author(self) -> Principal:
        """Gets the author property"""
        return self.properties.get("author", Principal())

    @property
    def content_anchor(self) -> ContentAnchor:
        """Gets the contentAnchor property"""
        return self.properties.get("contentAnchor", ContentAnchor())

    @property
    def created_date(self) -> Optional[datetime]:
        """Gets the createdDate property"""
        return self.properties.get("createdDate", datetime.min)

    @property
    def id_(self) -> Optional[str]:
        """Gets the id property"""
        return self.properties.get("id", None)

    @property
    def is_liked_by_user(self) -> Optional[bool]:
        """Gets the isLikedByUser property"""
        return self.properties.get("isLikedByUser", None)

    @property
    def is_reply(self) -> Optional[bool]:
        """Gets the isReply property"""
        return self.properties.get("isReply", None)

    @property
    def item_id(self) -> Optional[int]:
        """Gets the itemId property"""
        return self.properties.get("itemId", None)

    @property
    def like_count(self) -> Optional[int]:
        """Gets the likeCount property"""
        return self.properties.get("likeCount", None)

    @property
    def list_id(self) -> Optional[UUID]:
        """Gets the listId property"""
        return self.properties.get("listId", None)

    @property
    def mentions(self) -> ClientValueCollection[Identity]:
        """Gets the mentions property"""
        return self.properties.get("mentions", ClientValueCollection[Identity](Identity))

    @property
    def modified_date(self) -> Optional[datetime]:
        """Gets the modifiedDate property"""
        return self.properties.get("modifiedDate", datetime.min)

    @property
    def parent_id(self) -> Optional[str]:
        """Gets the parentId property"""
        return self.properties.get("parentId", None)

    @property
    def relative_created_date(self) -> Optional[str]:
        """Gets the relativeCreatedDate property"""
        return self.properties.get("relativeCreatedDate", None)

    @property
    def reply_count(self) -> Optional[int]:
        """Gets the replyCount property"""
        return self.properties.get("replyCount", None)

    @property
    def text(self) -> Optional[str]:
        """Gets the text property"""
        return self.properties.get("text", None)

    @property
    def id(self) -> Optional[str]:
        """Gets the id property"""
        return self.properties.get("id", None)

    @property
    def replies(self) -> EntityCollection[Comment]:
        """Gets the replies property"""
        from office365.sharepoint.comments.comment import Comment

        return self.properties.get(
            "replies", EntityCollection[Comment](self.context, Comment, ResourcePath("replies", self.resource_path))
        )
