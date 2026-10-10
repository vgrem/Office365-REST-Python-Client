from __future__ import annotations

from typing import Optional, Union

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata
from office365.sharepoint.entity import Entity
from office365.sharepoint.permissions.base_permissions import BasePermissions
from office365.sharepoint.permissions.roles.assignments.assignment import RoleAssignment
from office365.sharepoint.permissions.roles.assignments.collection import (
    RoleAssignmentCollection,
)
from office365.sharepoint.permissions.roles.definitions.definition import RoleDefinition
from office365.sharepoint.principal.principal import Principal
from office365.sharepoint.principal.users.user import User
from office365.sharepoint.sharing.role_type import RoleType


class SecurableObject(Entity):
    """An object that can be assigned security permissions."""

    def get_role_assignment(self, principal: Principal) -> RoleAssignment:
        """Retrieves the role assignment object (1) based on the specified user or group

        Args:
            principal (Principal): Specifies the user or group of the role assignment.
        """
        return_type = RoleAssignment(self.context)
        self.role_assignments.add_child(return_type)

        def _principal_loaded():
            return_type.set_property("PrincipalId", principal.id)

        principal.ensure_property("Id").after_execute(lambda _: _principal_loaded())
        return return_type

    def add_role_assignment(self, principal: Union[Principal, str], role: Union[RoleDefinition, RoleType]) -> Self:
        """Adds a role assignment to securable resource.

        Args:
            principal (RoleDefinition or int): Specifies the role definition or role type.
            role (Principal or str): Specifies the user or group of the role assignment.
        """

        if not isinstance(principal, Principal):
            principal = self.context.web.site_users.get_by_principal_name(principal)

        if not isinstance(role, RoleDefinition):
            role = self.context.web.role_definitions.get_by_type(role)

        def _ensure_role_def():
            role.ensure_property("Id").after_execute(lambda _: _add_role_assignment())

        def _add_role_assignment():
            if principal.id is not None and role.id is not None:
                self.role_assignments.add_role_assignment(principal.id, role.id)

        principal.ensure_property("Id").after_execute(lambda _: _ensure_role_def())
        return self

    def remove_role_assignment(self, principal: Principal | str, role_def: RoleDefinition | RoleType) -> Self:
        """Removes a role assignment from a securable resource.

        Args:
            principal (Principal): Specifies the user or group of the role assignment.
            role_def (RoleDefinition): Specifies the role definition of the role assignment.
        """
        if not isinstance(principal, Principal):
            principal = self.context.web.site_users.get_by_principal_name(principal)

        if not isinstance(role_def, RoleDefinition):
            role_def = self.context.web.role_definitions.get_by_type(role_def)

        def _remove_role_assignment():
            if principal.id is not None and role_def.id is not None:
                self.role_assignments.remove_role_assignment(principal.id, role_def.id)

        def _ensure_role_def():
            role_def.ensure_property("Id").after_execute(lambda _: _remove_role_assignment())

        principal.ensure_property("Id").after_execute(lambda _: _ensure_role_def())
        return self

    def grant_access(self, principal: Union[Principal, str], role: Union[RoleDefinition, RoleType]) -> Self:
        """Grants a role to a user or group on this securable object.

        A discoverable wrapper around :meth:`add_role_assignment`, reads as
        ``target.grant_access("user@contoso.com", RoleType.Contributor)``. The
        principal and role are resolved lazily and the request is queued; run
        ``execute_query()`` to send it.

        Args:
            principal (Principal or str): A user/group login name, or a
                :class:`~office365.sharepoint.principal.principal.Principal`
                (for example :class:`~office365.sharepoint.principal.users.user.User`).
            role (RoleDefinition or RoleType): The role to grant.

        Returns:
            Self: The securable object for method chaining.
        """
        return self.add_role_assignment(principal, role)

    def revoke_access(self, principal: Union[Principal, str], role: Union[RoleDefinition, RoleType]) -> Self:
        """Revokes a role previously granted to a user or group on this securable object.

        A discoverable wrapper around :meth:`remove_role_assignment`, reads as
        ``target.revoke_access("user@contoso.com", RoleType.Contributor)``. The
        request is queued; run ``execute_query()`` to send it.

        Args:
            principal (Principal or str): A user/group login name, or a
                :class:`~office365.sharepoint.principal.principal.Principal`
                (for example :class:`~office365.sharepoint.principal.users.user.User`).
            role (RoleDefinition or RoleType): The role to revoke.

        Returns:
            Self: The securable object for method chaining.
        """
        return self.remove_role_assignment(principal, role)

    def break_role_inheritance(self, copy_role_assignments=True, clear_sub_scopes=True):
        """Creates unique role assignments for the securable object. If the securable object already has
        unique role assignments, the protocol server MUST NOT alter any role assignments.

        Args:
            clear_sub_scopes (bool): If the securable object is a site (2), and the clearSubscopes parameter is "true",
                the role assignments for all child securable objects in the current site (2) and in
                the sites that inherit role assignments from the current site (2) MUST be cleared
                and those securable objects inherit role assignments from the current site (2)
                after this call.
                If the securable object is a site (2), and the clearSubscopes parameter is "false",
                the role assignments for all child securable objects that do not inherit role
                assignments from their parent object (1) MUST remain unchanged.
                If the securable object is not a site (2), and the clearSubscopes parameter is
                "true", the role assignments for all child securable objects MUST be cleared and
                those securable objects inherit role assignments from the current securable object
                after this call.
                If the securable object is not a site, and the clearSubscopes parameter is "false",
                the role assignments for all child securable objects that do not inherit role
                assignments from their parent object (1) MUST remain unchanged.
            copy_role_assignments (bool): Specifies whether to copy the role assignments from the parent securable
                object.If the value is "false", the collection of role assignments MUST
                contain only 1 role assignment containing the current user after the operation.
        """
        payload = {
            "copyRoleAssignments": copy_role_assignments,
            "clearSubscopes": clear_sub_scopes,
        }
        qry = ServiceOperationQuery(self, "BreakRoleInheritance", None, payload, None, None)
        self.context.add_query(qry)
        return self

    def reset_role_inheritance(self) -> Self:
        """Resets the role inheritance for the securable object and inherits role assignments from
        the parent securable object."""
        qry = ServiceOperationQuery(self, "ResetRoleInheritance", None, None, None, None)
        self.context.add_query(qry)
        return self

    def get_user_effective_permissions(self, user: str | User) -> ClientResult[BasePermissions]:
        """Returns the user permissions for secured object.

        Args:
            user (str or User): Specifies the user login name or User object.
        """
        return_type = ClientResult(self.context, BasePermissions())

        def _get_user_effective_permissions(login_name: str) -> None:
            qry = ServiceOperationQuery(
                self,
                "GetUserEffectivePermissions",
                [login_name],
                None,
                None,
                return_type,
            )
            self.context.add_query(qry)

        if isinstance(user, User):

            def _user_loaded():
                assert user.login_name is not None
                _get_user_effective_permissions(user.login_name)

            user.ensure_property("LoginName").after_execute(lambda _: _user_loaded())
        else:
            _get_user_effective_permissions(user)
        return return_type

    @property
    def has_unique_role_assignments(self) -> Optional[bool]:
        """Specifies whether the role assignments are uniquely defined for this securable object or inherited from a
        parent securable object. If the value is "false", role assignments are inherited from a parent securable
        object.
        """
        return self.properties.get("HasUniqueRoleAssignments", None)

    @odata(name="FirstUniqueAncestorSecurableObject")
    @property
    def first_unique_ancestor_securable_object(self) -> SecurableObject:
        """Specifies the object where role assignments for this object are defined"""
        return self.properties.get(
            "FirstUniqueAncestorSecurableObject",
            SecurableObject(
                self.context,
                ResourcePath("FirstUniqueAncestorSecurableObject", self.resource_path),
            ),
        )

    @odata(name="RoleAssignments")
    @property
    def role_assignments(self) -> RoleAssignmentCollection:
        """The role assignments for the securable object."""
        return self.properties.get(
            "RoleAssignments",
            RoleAssignmentCollection(self.context, ResourcePath("RoleAssignments", self.resource_path)),
        )

    @property
    def shield_add_role_assignment_pushdown(self) -> Optional[bool]:
        """Gets the ShieldAddRoleAssignmentPushdown property"""
        return self.properties.get("ShieldAddRoleAssignmentPushdown", None)
