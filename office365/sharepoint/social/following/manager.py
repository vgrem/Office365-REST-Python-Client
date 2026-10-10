from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.social.actor import SocialActor

if TYPE_CHECKING:
    from office365.sharepoint.social.actor_info import SocialActorInfo


class SocialFollowingManager(Entity):
    """The SocialFollowingManager class provides properties and methods for managing a user's list of followed actors.
    Actors can be users, documents, sites, and tags."""

    def __init__(self, context):
        super().__init__(context, ResourcePath("SP.Social.SocialFollowingManager"))

    def get_followers(self) -> ClientResult[ClientValueCollection[SocialActor]]:
        """
        The GetFollowers method returns the users who are followers of the current user.
        """
        return_type = ClientResult(self.context, ClientValueCollection(SocialActor))
        qry = ServiceOperationQuery(self, "GetFollowers", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_suggestions(self) -> ClientResult[ClientValueCollection[SocialActor]]:
        """
        The GetSuggestions method returns a list of actors that are suggestions for the current user to follow.
        """
        return_type = ClientResult(self.context, ClientValueCollection(SocialActor))
        qry = ServiceOperationQuery(self, "GetSuggestions", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def followed_documents_uri(self) -> Optional[str]:
        """Gets the FollowedDocumentsUri property"""
        return self.properties.get("FollowedDocumentsUri", None)

    @property
    def followed_sites_uri(self) -> Optional[str]:
        """Gets the FollowedSitesUri property"""
        return self.properties.get("FollowedSitesUri", None)

    @property
    def entity_type_name(self):
        return "SP.Social.SocialFollowingManager"

    def follow(self, actor: SocialActorInfo) -> ClientResult[int]:
        """Follow operation.

        Args:
            actor (SocialActorInfo):
                actor parameter
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "Follow", None, {"actor": actor}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_followed(self, types: int) -> ClientResult[ClientValueCollection[SocialActor]]:
        """GetFollowed operation.

        Args:
            types (int):
                types parameter
        """
        from office365.sharepoint.social.actor import SocialActor

        return_type = ClientResult(self.context, ClientValueCollection[SocialActor]())
        qry = ServiceOperationQuery(self, "GetFollowed", None, {"types": types}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_followed_count(self, types: int) -> ClientResult[int]:
        """GetFollowedCount operation.

        Args:
            types (int):
                types parameter
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "GetFollowedCount", None, {"types": types}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def is_followed(self, actor: SocialActorInfo) -> ClientResult[bool]:
        """IsFollowed operation.

        Args:
            actor (SocialActorInfo):
                actor parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "IsFollowed", None, {"actor": actor}, None, return_type)
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

    def stop_following(self, actor: SocialActorInfo) -> ClientResult[bool]:
        """StopFollowing operation.

        Args:
            actor (SocialActorInfo):
                actor parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "StopFollowing", None, {"actor": actor}, None, return_type)
        self.context.add_query(qry)
        return return_type
