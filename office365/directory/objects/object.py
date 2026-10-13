from __future__ import annotations

from datetime import datetime

from typing_extensions import Self

from office365.directory.quotas import IDENTITY_QUOTAS
from office365.entity import Entity
from office365.runtime.client_result import ClientResult
from office365.runtime.limits import limit
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata


@limit(*IDENTITY_QUOTAS)
class DirectoryObject(Entity):
    """Represents an Azure Active Directory object. The directoryObject type is the base type for many other
    directory entity types."""

    def check_member_objects(self, ids: list[str] | None = None) -> ClientResult[StringCollection]:
        """Check for membership in a list of group IDs, administrative unit IDs, or directory role IDs, for the IDs of
        the specified user, group, service principal, organizational contact, device, or directory object.

        Args:
            ids (list[str]): The unique identifiers for the objects
        """
        return_type = ClientResult(self.context, StringCollection())
        payload = {"ids": StringCollection(ids or [])}
        qry = ServiceOperationQuery(self, "checkMemberObjects", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_member_objects(self, security_enabled_only: bool = True) -> ClientResult[StringCollection]:
        """Returns all the groups and directory roles that a user, group, or directory object is a member of.
        This function is transitive.

        Args:
            security_enabled_only (bool):
        """
        return_type = ClientResult(self.context, StringCollection())
        payload = {"securityEnabledOnly": security_enabled_only}
        qry = ServiceOperationQuery(self, "getMemberObjects", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_member_groups(self, security_enabled_only: bool = True) -> ClientResult[StringCollection]:
        """Return all the groups that the specified user, group, or directory object is a member of. This function is
        transitive.

        Args:
            security_enabled_only (bool): true to specify that only security groups that the entity is a member of
              should be returned; false to specify that all groups and directory roles that the entity is a
                member of should be returned. true can be specified only for users or service principals to return
                security-enabled groups.
        """
        return_type = ClientResult(self.context, StringCollection())
        payload = {"securityEnabledOnly": security_enabled_only}
        qry = ServiceOperationQuery(self, "getMemberGroups", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def check_member_groups(self, group_ids: list[str] | None = None) -> ClientResult[StringCollection]:
        """Check for membership in the specified list of groups. Returns from the list those groups of which
        the specified group has a direct or transitive membership.

        You can check up to a maximum of 20 groups per request. This function supports Microsoft 365 and other types
        of groups provisioned in Azure AD. Note that Microsoft 365 groups cannot contain groups.
        So membership in a Microsoft 365 group is always direct.

        Args:
            group_ids (list[str]): A collection that contains the object IDs of the groups in which to check
              membership. Up to 20 groups may be specified.
        """
        return_type = ClientResult(self.context, StringCollection())
        payload = {"groupIds": group_ids}
        qry = ServiceOperationQuery(self, "checkMemberGroups", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def restore(self) -> Self:
        """
        Restore a recently deleted application, group, servicePrincipal, administrative unit, or user object from
        deleted items. If an item was accidentally deleted, you can fully restore the item. This is not applicable
        to security groups, which are deleted permanently.

        A recently deleted item will remain available for up to 30 days. After 30 days, the item is permanently deleted.
        """
        qry = ServiceOperationQuery(self, "restore")
        self.context.add_query(qry)
        return self

    @odata(name="deletedDateTime")
    @property
    def deleted_datetime(self) -> datetime:
        """Date and time when this object was deleted. Always null when the object hasn't been deleted."""
        return self.properties.get("deletedDateTime", datetime.min)

    @odata(name="deletedDateTime")
    @property
    def deleted_date_time(self) -> datetime:
        """Gets the deletedDateTime property"""
        return self.properties.get("deletedDateTime", datetime.min)

    @property
    def display_name(self) -> str | None:
        """The display name of the directory object.

        The base ``directoryObject`` type does not declare ``displayName`` itself, but
        almost every concrete type Graph returns (user, group, application, service
        principal, device, ...) includes it. Surfacing it here keeps the heterogeneous
        collections and navigations (``memberOf``, ``ownedObjects``, ``manager``, ...)
        usable through a typed property instead of a raw ``getattr``/``properties`` read.
        """
        return self.properties.get("displayName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DirectoryObject"
