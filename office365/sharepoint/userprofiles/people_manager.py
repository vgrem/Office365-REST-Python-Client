from __future__ import annotations

from typing import Callable, List, Optional, Union
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.paths.v3.static import StaticPath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.principal.users.user import User
from office365.sharepoint.userprofiles.hash_tag_col import HashTagCollection
from office365.sharepoint.userprofiles.person_properties import PersonProperties
from office365.sharepoint.userprofiles.personal_site_creation_priority import (
    PersonalSiteCreationPriority,
)


def _ensure_user(user: Union[str, User], action: Optional[Callable[[str], None]] = None) -> None:
    if isinstance(user, User):
        user.ensure_property("LoginName").after_execute(lambda _: action(user.login_name))  # type: ignore[arg-type]
    else:
        action(user)  # type: ignore[arg-type]


class PeopleManager(Entity):
    """Provides methods for operations related to people."""

    @property
    def resource_path(self):
        if self._resource_path is None:
            self._resource_path = StaticPath("SP.UserProfiles.PeopleManager")
        return self._resource_path

    @staticmethod
    def get_trending_tags(context) -> HashTagCollection:
        """Gets a collection of the 20 (or fewer) most popular hash tags over the past week.
        The returned collection is sorted in descending order of frequency of use.

        Args:
            context (office365.sharepoint.client_context.ClientContext):
        """
        return_type = HashTagCollection(context)
        manager = PeopleManager(context)
        qry = ServiceOperationQuery(manager, "GetTrendingTags", None, None, None, return_type, True)
        context.add_query(qry)
        return return_type

    def get_user_onedrive_quota_max(self, account_name: str) -> ClientResult[int]:
        """Args:
        account_name (str): Account name of the specified user.
        """
        return_type = ClientResult(self.context, int())
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "GetUserOneDriveQuotaMax", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def am_i_following(self, account_name: str) -> ClientResult[bool]:
        """Checks whether the current user is following the specified user.

        Args:
            account_name (str): Account name of the specified user.
        """
        result = ClientResult(self.context, bool())
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "AmIFollowing", params, None, None, result)
        self.context.add_query(qry)
        return result

    def get_followers_for(self, account: Union[str, User]) -> EntityCollection[PersonProperties]:
        """Gets the people who are following the specified user.

        Args:
            account (str|User): Account name of the specified user.
        """
        return_type = EntityCollection(self.context, PersonProperties)

        def _get_followers_for(account_name: str) -> None:
            params = {"accountName": account_name}
            qry = ServiceOperationQuery(self, "GetFollowersFor", params, None, None, return_type)
            self.context.add_query(qry)

        if isinstance(account, User):

            def _account_loaded():
                login_name = account.login_name
                assert login_name is not None
                _get_followers_for(login_name)

            account.ensure_property("LoginName").after_execute(lambda _: _account_loaded())
        else:
            _get_followers_for(account)
        return return_type

    def get_user_information(self, account_name: str, site_id: str) -> ClientResult[dict]:
        """Args:
        account_name (str): Account name of the specified user.
        site_id (str): Site Identifier.
        """
        return_type = ClientResult(self.context, {})
        params = {"accountName": account_name, "siteId": site_id}
        qry = ServiceOperationQuery(self, "GetSPUserInformation", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def follow(self, account_name: str) -> Self:
        """Add the specified user to the current user's list of followed users.

        Args:
            account_name (str): Account name of the specified user.
        """
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "Follow", params, None, None, None)
        self.context.add_query(qry)
        return self

    def stop_following(self, account_name: str) -> Self:
        """Remove the specified user from the current user's list of followed users.

        Args:
            account_name (str):
        """
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "StopFollowing", params)
        self.context.add_query(qry)
        return self

    def stop_following_tag(self, value: str) -> Self:
        """The StopFollowingTag method sets the current user to no longer be following the specified tag.

        Args:
            value (str): Specifies the tag by its GUID
        """
        params = {"value": value}
        qry = ServiceOperationQuery(self, "StopFollowingTag", params)
        self.context.add_query(qry)
        return self

    def get_user_profile_properties(self, user: Union[str, User]) -> ClientResult[dict]:
        """Gets the specified user profile properties for the specified user.

        Args:
            user (str or User): User or Login name of the specified user.
        """
        return_type = ClientResult(self.context, {})

        def _get_user_profile_properties(account_name: str) -> None:
            params = {"accountName": account_name}
            qry = ServiceOperationQuery(self, "GetUserProfileProperties", params, None, None, return_type)
            self.context.add_query(qry)

        _ensure_user(user, _get_user_profile_properties)
        return return_type

    def get_properties_for(self, account: Union[str, User]) -> PersonProperties:
        """Gets user properties for the specified user.

        Args:
            account (str or User): Specifies the User object or its login name.
        """
        return_type = PersonProperties(self.context)

        def _get_properties_for(account_name: str) -> None:
            params = {"accountName": account_name}
            qry = ServiceOperationQuery(self, "GetPropertiesFor", params, None, None, return_type)
            self.context.add_query(qry)

        _ensure_user(account, _get_properties_for)
        return return_type

    def get_default_document_library(
        self,
        user: Union[str, User],
        create_site_if_not_exists=False,
        site_creation_priority=PersonalSiteCreationPriority.Low,
    ) -> ClientResult[str]:
        """Gets the OneDrive Document library path for a given user.

        Args:
            user (str or User user_or_name): The login name of the user whose OneDrive URL is required.
            For example, "i:0#.f|membership|admin@contoso.sharepoint.com”.
            create_site_if_not_exists (bool): If this value is set to true and the site doesn't exist, the site will
            get created.
            site_creation_priority (int): The priority for site creation. Type: PersonalSiteCreationPriority
        """
        return_type = ClientResult[str](self.context)

        def _get_default_document_library(account_name: str) -> None:
            params = {
                "accountName": account_name,
                "createSiteIfNotExists": create_site_if_not_exists,
                "siteCreationPriority": site_creation_priority,
            }
            qry = ServiceOperationQuery(self, "GetDefaultDocumentLibrary", params, None, None, return_type)
            self.context.add_query(qry)

        _ensure_user(user, _get_default_document_library)
        return return_type

    def get_people_followed_by(self, account_name: str) -> EntityCollection[PersonProperties]:
        """The GetPeopleFollowedBy method returns a  list of PersonProperties objects for people who the specified user
        is following. This method can result in exceptions for conditions such as null arguments or if the specified
        user cannot be found.

        Args:
            account_name (str): Account name of the specified user.
        """
        return_type = EntityCollection(self.context, PersonProperties)
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "GetPeopleFollowedBy", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_my_followers(self) -> EntityCollection[PersonProperties]:
        """
        This method returns a list of PersonProperties objects for the people who are following the current user.
        """
        return_type = EntityCollection(self.context, PersonProperties)
        qry = ServiceOperationQuery(self, "GetMyFollowers", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def follow_tag(self, value: str) -> Self:
        """The FollowTag method sets the current user to be following the specified tag.

        Args:
            value (str): Specifies the tag by its GUID.
        """

        qry = ServiceOperationQuery(self, "FollowTag", [value])
        self.context.add_query(qry)
        return self

    def hide_suggestion(self, account_name: str) -> Self:
        """The HideSuggestion method adds the specified user to list of rejected suggestions.

        Args:
            account_name (str): Specifies the user by account name.
        """
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "HideSuggestion", params)
        self.context.add_query(qry)
        return self

    def reset_user_onedrive_quota_to_default(self, account_name: str) -> ClientResult[str]:
        """Args:
        account_name (str): Specifies the user by account name.
        """
        return_type = ClientResult(self.context, str())
        params = {"accountName": account_name}
        qry = ServiceOperationQuery(self, "ResetUserOneDriveQuotaToDefault", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_my_profile_picture(self, picture: bytes) -> Self:
        """The SetMyProfilePicture method uploads and sets the user profile picture. Pictures in bmp, jpg and png formats
        and up to 5,000,000 bytes are supported. A user can upload a picture only to the user's own profile.

        Args:
            picture (str or bytes): Binary content of an image file
        """
        qry = ServiceOperationQuery(self, "SetMyProfilePicture", None, {"picture": picture})
        self.context.add_query(qry)
        return self

    def set_user_onedrive_quota(self, account_name: str, new_quota: int, new_quota_warning: int) -> ClientResult[str]:
        """Args:
        account_name (str):
        new_quota (long):
        new_quota_warning (long):
        """
        return_type = ClientResult(self.context, str())
        payload = {
            "accountName": account_name,
            "newQuota": new_quota,
            "newQuotaWarning": new_quota_warning,
        }
        qry = ServiceOperationQuery(self, "SetUserOneDriveQuota", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_multi_valued_profile_property(
        self, account_name: str, property_name: str, property_values: List[str]
    ) -> Self:
        """Sets the value of a multivalued user profile property.

        Args:
            account_name (str): Specifies the user by account name.
            property_name (str): The name of the property to set.
            property_values (list[str]): The values being set on the property.
        """
        payload = {
            "accountName": account_name,
            "propertyName": property_name,
            "propertyValues": StringCollection(property_values),
        }
        qry = ServiceOperationQuery(self, "SetMultiValuedProfileProperty", None, payload)
        self.context.add_query(qry)
        return self

    def set_single_value_profile_property(self, account_name: str, property_name: str, property_value: str) -> Self:
        """Sets the value of a user profile property.

        Args:
            account_name (str): Specifies the user by account name.
            property_name (str): The name of the property to set.
            property_value (str): The value being set on the property.
        """
        payload = {
            "accountName": account_name,
            "propertyName": property_name,
            "propertyValue": property_value,
        }
        qry = ServiceOperationQuery(self, "SetSingleValueProfileProperty", None, payload)
        self.context.add_query(qry)
        return self

    @property
    def entity_type_name(self):
        return "SP.UserProfiles.PeopleManager"

    @property
    def edit_profile_link(self) -> Optional[str]:
        """Gets the EditProfileLink property"""
        return self.properties.get("EditProfileLink", None)

    @property
    def is_my_people_list_public(self) -> Optional[bool]:
        """Gets the IsMyPeopleListPublic property"""
        return self.properties.get("IsMyPeopleListPublic", None)

    def am_i_followed_by(self, account_name: str) -> ClientResult[bool]:
        """AmIFollowedBy operation.

        Args:
            account_name (str):
                accountName parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = FunctionQuery(self, "AmIFollowedBy", [account_name], return_type)
        self.context.add_query(qry)
        return return_type

    def get_followed_tags(self, ctags_to_fetch: int) -> ClientResult[StringCollection]:
        """GetFollowedTags operation.

        Args:
            ctags_to_fetch (int):
                cTagsToFetch parameter
        """
        return_type = ClientResult(self.context, StringCollection())
        qry = FunctionQuery(self, "GetFollowedTags", [ctags_to_fetch], return_type)
        self.context.add_query(qry)
        return return_type

    def get_user_profile_property_for(self, account_name: str, property_name: str) -> ClientResult[str]:
        """GetUserProfilePropertyFor operation.

        Args:
            account_name (str):
                accountName parameter
            property_name (str):
                propertyName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetUserProfilePropertyFor", [account_name, property_name], return_type)
        self.context.add_query(qry)
        return return_type

    def hard_delete_user_profile(self, account_name: str, user_id: UUID) -> ClientResult[bool]:
        """HardDeleteUserProfile operation.

        Args:
            account_name (str):
                accountName parameter
            user_id (UUID):
                userId parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self, "HardDeleteUserProfile", None, {"accountName": account_name, "userId": user_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type
