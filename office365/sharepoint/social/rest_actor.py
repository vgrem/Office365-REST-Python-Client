from __future__ import annotations

from typing import Optional

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.social.actor import SocialActor


class SocialRestActor(Entity):
    """The SocialRestActor type contains information about an actor retrieved from server. An actor is a user, document,
    site, or tag. The SocialRestActor type is available when the protocol client sends an OData request to a protocol
    server using [MS-CSOMREST]. It is not available using [MS-CSOM]."""

    @property
    def me(self) -> SocialActor:
        """The Me property provides access to the current user.
        See section 3.1.5.3 for details on the SocialActor type"""
        return self.properties.get("Me", SocialActor())

    @property
    def entity_type_name(self):
        return "SP.Social.SocialRestActor"

    @property
    def followable_item(self) -> Optional[str]:
        """Gets the FollowableItem property"""
        return self.properties.get("FollowableItem", None)

    @property
    def followable_item_actor(self) -> SocialActor:
        """Gets the FollowableItemActor property"""
        from office365.sharepoint.social.actor import SocialActor

        return self.properties.get("FollowableItemActor", SocialActor())

    def unread_mention_count(self) -> ClientResult[int]:
        """UnreadMentionCount operation."""
        return_type = ClientResult(self.context, int())
        qry = FunctionQuery(self, "UnreadMentionCount", [], return_type)
        self.context.add_query(qry)
        return return_type
