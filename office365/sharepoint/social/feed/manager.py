from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.social.actor import SocialActor
from office365.sharepoint.social.attachment import SocialAttachment
from office365.sharepoint.social.feed.feed import SocialFeed
from office365.sharepoint.social.posts.creation_data import SocialPostCreationData
from office365.sharepoint.social.thread import SocialThread

if TYPE_CHECKING:
    from office365.sharepoint.social.feedoptions import SocialFeedOptions


class SocialFeedManager(Entity):
    """The SocialFeedManager class provides access to social feeds. It provides methods to create posts,
    delete posts, read posts, and perform other operations on posts."""

    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = ResourcePath("SP.Social.SocialFeedManager")
        super().__init__(context, resource_path)

    def create_post(self, target_id: Optional[str] = None, creation_data: Optional[SocialPostCreationData] = None):
        """The CreatePost method creates a post in the current user's feed, in the specified user's feed, or in
        the specified thread. This method returns a new or a modified thread.

        Args:
            target_id (str or None): Optional, specifies the target of the post. If this parameter is null, the
                post is created as a root post in the current user's feed. If this parameter is set to a site (2)
                URL or a site (2) actor identification, the post is created as a root post in the specified site (2)
                feed. If this parameter is set to a thread identification, the post is created as a reply post in
                the specified thread.
            creation_data (SocialPostCreationData): Specifies the text and details of the post.
        """
        return_type = ClientResult(self.context, SocialThread())
        payload = {"targetId": target_id, "creationData": creation_data}
        qry = ServiceOperationQuery(self, "CreatePost", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def delete_post(self, post_id: str) -> ClientResult[SocialThread]:
        """The DeletePost method deletes the specified post. This method returns a digest of the modified thread.
        If the entire thread is deleted, this method returns null.

        Args:
            post_id (str): Specifies the post to be deleted. The post identifier is specified in the
                SocialPost.Id property
        """
        return_type = ClientResult(self.context, SocialThread())
        payload = {"postId": post_id}
        qry = ServiceOperationQuery(self, "DeletePost", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_file_attachment(self, name, description, file_data):
        """Creates a file attachment for a future post.

        Args:
            name (str): The name of the file.
            description (str): An optional description of the file.
            file_data (str or bytes): A stream for reading the file data.
        """
        return_type = ClientResult(self.context, SocialAttachment())
        payload = {"name": name, "description": description, "fileData": file_data}
        qry = ServiceOperationQuery(self, "CreateFileAttachment", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_feed(self, feed_type=None, options=None):
        """The GetFeed method returns a feed for the current user. The feed consists of an array of message threads.
        Each thread consists of a root post and an array of reply posts. See section 3.1.5.17 for details on
        the SocialFeed type. The server selects a set of posts to return in the feed based on the type
        and options parameters, but this protocol does require any specific algorithm to select the set of posts
        from all posts that meet the specified type and options.

        Args:
            feed_type (int): Specifies the type of feed to be returned. Feeds can be viewed using a personal view,
                news view, timeline view, or likes view. If the type is not specified, GetFeed returns the news view.
            options (SocialFeedOptions): Specifies the maximum number of threads to get in the feed, the sort order
                of the threads, and how the threads are to be selected based on the date and time that the threads
                were created.
        """
        return_type = ClientResult(self.context, SocialFeed())
        payload = {"type": feed_type, "options": options}
        qry = ServiceOperationQuery(self, "GetFeed", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def owner(self) -> SocialActor:
        """The Owner property returns the current user."""
        return self.properties.get("Owner", SocialActor())

    @property
    def personal_site_portal_uri(self) -> Optional[str]:
        """The PersonalSitePortalUri property specifies the URI of the personal site portal."""
        return self.properties.get("PersonalSitePortalUri", None)

    @property
    def entity_type_name(self):
        return "SP.Social.SocialFeedManager"

    def create_image_attachment(self, name: str, description: str, image_data: bytes) -> ClientResult[SocialAttachment]:
        """CreateImageAttachment operation.

        Args:
            name (str):
                name parameter
            description (str):
                description parameter
            image_data (bytes):
                imageData parameter
        """
        from office365.sharepoint.social.attachment import SocialAttachment

        return_type = ClientResult(self.context, SocialAttachment())
        qry = ServiceOperationQuery(
            self,
            "CreateImageAttachment",
            None,
            {"name": name, "description": description, "imageData": image_data},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_all_likers(self, post_id: str) -> ClientResult[ClientValueCollection[SocialActor]]:
        """GetAllLikers operation.

        Args:
            post_id (str):
                postId parameter
        """
        from office365.sharepoint.social.actor import SocialActor

        return_type = ClientResult(self.context, ClientValueCollection[SocialActor]())
        qry = ServiceOperationQuery(self, "GetAllLikers", None, {"postId": post_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_feed_for(self, actor_id: str, options: SocialFeedOptions) -> ClientResult[SocialFeed]:
        """GetFeedFor operation.

        Args:
            actor_id (str):
                actorId parameter
            options (SocialFeedOptions):
                options parameter
        """
        from office365.sharepoint.social.feed.feed import SocialFeed

        return_type = ClientResult(self.context, SocialFeed())
        qry = ServiceOperationQuery(
            self, "GetFeedFor", None, {"actorId": actor_id, "options": options}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_full_thread(self, thread_id: str) -> ClientResult[SocialThread]:
        """GetFullThread operation.

        Args:
            thread_id (str):
                threadId parameter
        """
        from office365.sharepoint.social.thread import SocialThread

        return_type = ClientResult(self.context, SocialThread())
        qry = ServiceOperationQuery(self, "GetFullThread", None, {"threadId": thread_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_mentions(self, clear_unread_mentions: bool, options: SocialFeedOptions) -> ClientResult[SocialFeed]:
        """GetMentions operation.

        Args:
            clear_unread_mentions (bool):
                clearUnreadMentions parameter
            options (SocialFeedOptions):
                options parameter
        """
        from office365.sharepoint.social.feed.feed import SocialFeed

        return_type = ClientResult(self.context, SocialFeed())
        qry = ServiceOperationQuery(
            self,
            "GetMentions",
            None,
            {"clearUnreadMentions": clear_unread_mentions, "options": options},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_preview(self, item_url: str) -> ClientResult[SocialAttachment]:
        """GetPreview operation.

        Args:
            item_url (str):
                itemUrl parameter
        """
        from office365.sharepoint.social.attachment import SocialAttachment

        return_type = ClientResult(self.context, SocialAttachment())
        qry = ServiceOperationQuery(self, "GetPreview", None, {"itemUrl": item_url}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_preview_image(self, url: str, key: str, iv: str) -> ClientResult[bytes]:
        """GetPreviewImage operation.

        Args:
            url (str):
                url parameter
            key (str):
                key parameter
            iv (str):
                iv parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "GetPreviewImage", [url, key, iv], return_type, return_raw_content=True)
        self.context.add_query(qry)
        return return_type

    def get_unread_mention_count(self) -> ClientResult[int]:
        """GetUnreadMentionCount operation."""
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "GetUnreadMentionCount", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def like_post(self, post_id: str) -> ClientResult[SocialThread]:
        """LikePost operation.

        Args:
            post_id (str):
                postId parameter
        """
        from office365.sharepoint.social.thread import SocialThread

        return_type = ClientResult(self.context, SocialThread())
        qry = ServiceOperationQuery(self, "LikePost", None, {"postId": post_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def lock_thread(self, thread_id: str) -> ClientResult[SocialThread]:
        """LockThread operation.

        Args:
            thread_id (str):
                threadId parameter
        """
        from office365.sharepoint.social.thread import SocialThread

        return_type = ClientResult(self.context, SocialThread())
        qry = ServiceOperationQuery(self, "LockThread", None, {"threadId": thread_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def suppress_thread_notifications(self, thread_id: str) -> Self:
        """SuppressThreadNotifications operation.

        Args:
            thread_id (str):
                threadId parameter
        """
        qry = ServiceOperationQuery(self, "SuppressThreadNotifications", None, {"threadId": thread_id}, None, None)
        self.context.add_query(qry)
        return self

    def unlike_post(self, post_id: str) -> ClientResult[SocialThread]:
        """UnlikePost operation.

        Args:
            post_id (str):
                postId parameter
        """
        from office365.sharepoint.social.thread import SocialThread

        return_type = ClientResult(self.context, SocialThread())
        qry = ServiceOperationQuery(self, "UnlikePost", None, {"postId": post_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def unlock_thread(self, thread_id: str) -> ClientResult[SocialThread]:
        """UnlockThread operation.

        Args:
            thread_id (str):
                threadId parameter
        """
        from office365.sharepoint.social.thread import SocialThread

        return_type = ClientResult(self.context, SocialThread())
        qry = ServiceOperationQuery(self, "UnlockThread", None, {"threadId": thread_id}, None, return_type)
        self.context.add_query(qry)
        return return_type
