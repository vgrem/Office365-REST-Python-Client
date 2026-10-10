from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.v3.static import StaticPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity
from office365.sharepoint.userprofiles.user_profile import UserProfile

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class ProfileLoader(Entity):
    """The ProfileLoader class provides access to the current user's profile."""

    @property
    def resource_path(self):
        if self._resource_path is None:
            self._resource_path = StaticPath("SP.UserProfiles.ProfileLoader.GetProfileLoader")
        return self._resource_path

    @staticmethod
    def get_profile_loader(context: ClientContext) -> ProfileLoader:
        """
        The GetProfileLoader method returns a profile loader.
        """
        return_type = ProfileLoader(context)
        qry = ServiceOperationQuery(return_type, "GetProfileLoader", None, None, None, return_type, True)
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_owner_user_profile(context: ClientContext) -> UserProfile:
        """
        Gets the user profile for the Site owner.
        """
        return_type = UserProfile(context)
        qry = ServiceOperationQuery(
            ProfileLoader(context),
            "GetOwnerUserProfile",
            None,
            None,
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    def get_user_profile(self) -> UserProfile:
        """The GetUserProfile method returns the user profile for the current user."""
        result = UserProfile(self.context, ResourcePath("GetUserProfile", self.resource_path))
        qry = ServiceOperationQuery(self, "GetUserProfile", None, None, None, result)
        self.context.add_query(qry)
        return result

    @property
    def entity_type_name(self):
        return "SP.UserProfiles.ProfileLoader"

    def create_personal_site_enqueue_bulk(self, email_ids: list[str]) -> ClientResult[StringCollection]:
        """CreatePersonalSiteEnqueueBulk operation.

        Args:
            email_ids (list[str]):
                emailIDs parameter
        """
        return_type = ClientResult(self.context, StringCollection())
        qry = ServiceOperationQuery(
            self, "CreatePersonalSiteEnqueueBulk", None, {"emailIDs": StringCollection(email_ids)}, None, return_type
        )
        self.context.add_query(qry)
        return return_type
