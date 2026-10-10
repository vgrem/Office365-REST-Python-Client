from __future__ import annotations

from typing import Optional
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.social.actor import SocialActor


class SocialRestFollowingManager(Entity):
    """Provides methods for managing a user's list of followed actors (users, documents, sites, and tags)."""

    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = ResourcePath("SP.Social.SocialRestFollowingManager")
        super().__init__(context, resource_path)

    def followers(self) -> ClientResult[ClientValueCollection[SocialActor]]:
        """The Followers method retrieves the current user's list of followers. For details on the SocialActor type,
        see section 3.1.5.3."""
        return_type = ClientResult(self.context, ClientValueCollection(SocialActor))
        qry = ServiceOperationQuery(self, "Followers", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def my(self) -> SocialRestFollowingManager:
        """The My method gets a SocialRestActor object that represents the current user. See section 3.1.5.35 for
        details on the SocialRestActor type."""
        return SocialRestFollowingManager(self.context, ResourcePath("My", self.resource_path))

    @property
    def entity_type_name(self):
        return "SP.Social.SocialRestFollowingManager"

    @property
    def followed_documents_uri(self) -> Optional[str]:
        """Gets the FollowedDocumentsUri property"""
        return self.properties.get("FollowedDocumentsUri", None)

    @property
    def followed_sites_uri(self) -> Optional[str]:
        """Gets the FollowedSitesUri property"""
        return self.properties.get("FollowedSitesUri", None)

    @property
    def my_followed_documents_uri(self) -> Optional[str]:
        """Gets the MyFollowedDocumentsUri property"""
        return self.properties.get("MyFollowedDocumentsUri", None)

    @property
    def my_followed_sites_uri(self) -> Optional[str]:
        """Gets the MyFollowedSitesUri property"""
        return self.properties.get("MyFollowedSitesUri", None)

    @property
    def social_actor(self) -> SocialActor:
        """Gets the SocialActor property"""
        from office365.sharepoint.social.actor import SocialActor

        return self.properties.get("SocialActor", SocialActor())

    def follow(
        self, account_name: str, actor_type: int, content_uri: str, id_: str, tag_guid: UUID
    ) -> ClientResult[int]:
        """Follow operation.

        Args:
            account_name (str):
                AccountName parameter
            actor_type (int):
                ActorType parameter
            content_uri (str):
                ContentUri parameter
            id_ (str):
                Id parameter
            tag_guid (UUID):
                TagGuid parameter
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(
            self,
            "Follow",
            None,
            {
                "AccountName": account_name,
                "ActorType": actor_type,
                "ContentUri": content_uri,
                "Id": id_,
                "TagGuid": tag_guid,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def followed(self, types: int, count: int) -> ClientResult[ClientValueCollection[SocialActor]]:
        """Followed operation.

        Args:
            types (int):
                types parameter
            count (int):
                count parameter
        """
        from office365.sharepoint.social.actor import SocialActor

        return_type = ClientResult(self.context, ClientValueCollection[SocialActor]())
        qry = FunctionQuery(self, "Followed", [types, count], return_type)
        self.context.add_query(qry)
        return return_type

    def followed_count(self, types: int) -> ClientResult[int]:
        """FollowedCount operation.

        Args:
            types (int):
                types parameter
        """
        return_type = ClientResult(self.context, int())
        qry = FunctionQuery(self, "FollowedCount", [types], return_type)
        self.context.add_query(qry)
        return return_type

    def is_followed(
        self, account_name: str, actor_type: int, content_uri: str, id_: str, tag_guid: UUID
    ) -> ClientResult[bool]:
        """IsFollowed operation.

        Args:
            account_name (str):
                AccountName parameter
            actor_type (int):
                ActorType parameter
            content_uri (str):
                ContentUri parameter
            id_ (str):
                Id parameter
            tag_guid (UUID):
                TagGuid parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self,
            "IsFollowed",
            None,
            {
                "AccountName": account_name,
                "ActorType": actor_type,
                "ContentUri": content_uri,
                "Id": id_,
                "TagGuid": tag_guid,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def merge_followed_sites(self, followed_sites: str) -> ClientResult[str]:
        """MergeFollowedSites operation.

        Args:
            followed_sites (str):
                followedSites parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "MergeFollowedSites", None, {"followedSites": followed_sites}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def stop_following(self, account_name: str, actor_type: int, content_uri: str, id_: str, tag_guid: UUID) -> Self:
        """StopFollowing operation.

        Args:
            account_name (str):
                AccountName parameter
            actor_type (int):
                ActorType parameter
            content_uri (str):
                ContentUri parameter
            id_ (str):
                Id parameter
            tag_guid (UUID):
                TagGuid parameter
        """
        qry = ServiceOperationQuery(
            self,
            "StopFollowing",
            None,
            {
                "AccountName": account_name,
                "ActorType": actor_type,
                "ContentUri": content_uri,
                "Id": id_,
                "TagGuid": tag_guid,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def suggestions(self) -> ClientResult[ClientValueCollection[SocialActor]]:
        """Suggestions operation."""
        from office365.sharepoint.social.actor import SocialActor

        return_type = ClientResult(self.context, ClientValueCollection[SocialActor]())
        qry = FunctionQuery(self, "Suggestions", [], return_type)
        self.context.add_query(qry)
        return return_type
