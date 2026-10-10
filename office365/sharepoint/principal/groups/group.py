from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union, cast

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.principal.principal import Principal
from office365.sharepoint.utilities.principal_info import PrincipalInfo

if TYPE_CHECKING:
    from office365.sharepoint.principal.groups.collection import GroupCollection


class Group(Principal):
    """Represents a collection of members in a SharePoint site. A group is a type of SP.Principal."""

    def delete_object(self) -> Self:  # type: ignore[reportIncompatibleMethodOverride]
        """
        Deletes the group
        A custom operation since the default type SP.Group does not support HTTP DELETE method.
        """
        if self.id:
            self.parent_collection.remove_by_id(self.id)
        elif self.login_name:
            self.parent_collection.remove_by_login_name(self.login_name)
        else:

            def _remove_self(_):
                self.parent_collection.remove_by_id(self.id)

            self.ensure_property("Id").after_execute(_remove_self)
        return self

    def expand_to_principals(self, max_count: int = 10) -> ClientResult[ClientValueCollection[PrincipalInfo]]:
        """Expands current group to a collection of principals.

        Args:
            max_count (int): Specifies the maximum number of principals to be returned.
        """
        return_type = ClientResult(self.context, ClientValueCollection(PrincipalInfo))

        def _expand_to_principals():
            from office365.sharepoint.utilities.utility import Utility

            assert self.login_name is not None
            Utility.expand_groups_to_principals(self.context, [self.login_name], max_count, return_type)

        self.ensure_property("LoginName").after_execute(lambda _: _expand_to_principals())
        return return_type

    def set_user_as_owner(self, user: Union[int, Principal]) -> Self:
        """Sets the user as group owner

        Args:
            user (long or Principal): User object or identifier
        """

        def _set_user_as_owner(owner_id: int):
            qry = ServiceOperationQuery(self, "SetUserAsOwner", None, {"ownerId": owner_id})
            self.context.add_query(qry)

        if isinstance(user, Principal):
            user.ensure_property("Id").after_execute(
                lambda _: _set_user_as_owner(user.id) if user.id is not None else None
            )
        else:
            _set_user_as_owner(user)
        return self

    @property
    def parent_collection(self) -> GroupCollection:
        from office365.sharepoint.principal.groups.collection import GroupCollection

        return cast(GroupCollection, self._parent_collection)

    @property
    def allow_members_edit_membership(self) -> Optional[bool]:
        """Specifies whether a member of the group can add and remove members from the group"""
        return self.properties.get("AllowMembersEditMembership", None)

    @property
    def allow_request_to_join_leave(self) -> Optional[bool]:
        """Specifies whether to allow users to request to join or leave in the group."""
        return self.properties.get("AllowRequestToJoinLeave", None)

    @property
    def auto_accept_request_to_join_leave(self) -> Optional[bool]:
        """Specifies whether requests to join or leave the group are automatically accepted"""
        return self.properties.get("AutoAcceptRequestToJoinLeave", None)

    @property
    def can_current_user_edit_membership(self) -> Optional[bool]:
        """Specifies whether the current user can add and remove members from the group."""
        return self.properties.get("CanCurrentUserEditMembership", None)

    @property
    def can_current_user_manage_group(self) -> Optional[bool]:
        """Gets a Boolean value that indicates whether the current user can manage the group."""
        return self.properties.get("CanCurrentUserManageGroup", None)

    @property
    def can_current_user_view_membership(self) -> Optional[bool]:
        """Specifies whether the current user can view the membership of the group."""
        return self.properties.get("CanCurrentUserViewMembership", None)

    @property
    def only_allow_members_view_membership(self) -> Optional[bool]:
        """Specifies whether viewing the membership of the group is restricted to members of the group."""
        return self.properties.get("OnlyAllowMembersViewMembership", None)

    @property
    def owner_title(self) -> Optional[str]:
        """Specifies the name of the owner of the group."""
        return self.properties.get("OwnerTitle", None)

    @property
    def request_to_join_leave_email_setting(self) -> Optional[str]:
        """Specifies the e-mail address to which requests to join or leave the group are sent."""
        return self.properties.get("RequestToJoinLeaveEmailSetting", None)

    @property
    def owner(self) -> Principal:
        """Specifies the owner of the group."""
        return self.properties.get("Owner", Principal(self.context, ResourcePath("Owner", self.resource_path)))

    @property
    def users(self):
        """Gets a collection of user objects that represents all of the members in the group."""
        from office365.sharepoint.principal.users.collection import UserCollection

        return self.properties.get(
            "Users",
            UserCollection(self.context, ResourcePath("Users", self.resource_path)),
        )

    @property
    def contains_current_user(self) -> Optional[bool]:
        """Gets the ContainsCurrentUser property"""
        return self.properties.get("ContainsCurrentUser", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)
