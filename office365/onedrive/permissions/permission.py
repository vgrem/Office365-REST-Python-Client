from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity
from office365.onedrive.drives.recipient import DriveRecipient
from office365.onedrive.listitems.item_reference import ItemReference
from office365.onedrive.permissions.sharepoint_identity_set import SharePointIdentitySet
from office365.onedrive.permissions.sharing_invitation import SharingInvitation
from office365.onedrive.permissions.sharing_link import SharingLink
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.onedrive.permissions.collection import PermissionCollection


class Permission(Entity):
    """The Permission resource provides information about a sharing permission granted for a DriveItem resource."""

    def grant(self, recipients: List[str], roles: List[str]) -> PermissionCollection:
        """Grant users access to a link represented by a permission.

        Args:
            recipients (list[str]): A collection of recipients who will receive access.
            roles (list[str]): If the link is an "existing access" link, specifies roles to be granted to the users.
              Otherwise must match the role of the link.
        """
        from office365.onedrive.permissions.collection import PermissionCollection

        payload = {
            "recipients": ClientValueCollection(DriveRecipient, [DriveRecipient.from_email(r) for r in recipients]),
            "roles": StringCollection(roles),
        }

        return_type = PermissionCollection(self.context, ResourcePath("permissions", self.resource_path))
        qry = ServiceOperationQuery(self, "grant", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def invitation(self) -> SharingInvitation:
        """For user type permissions, the details of the users & applications for this permission."""
        return self.properties.get("invitation", SharingInvitation())

    @odata(name="grantedTo")
    @property
    def granted_to(self) -> IdentitySet:
        """For user type permissions, the details of the users & applications for this permission."""
        return self.properties.get("grantedTo", IdentitySet())

    @odata(name="grantedToV2")
    @property
    def granted_to_v2(self) -> SharePointIdentitySet:
        """For user type permissions, the details of the users and applications for this permission."""
        return self.properties.get("grantedToV2", SharePointIdentitySet())

    @odata(name="grantedToIdentities")
    @property
    def granted_to_identities(self) -> ClientValueCollection[IdentitySet]:
        """For link type permissions, the details of the users to whom permission was granted. Read-only."""
        return self.properties.get("grantedToIdentities", ClientValueCollection(IdentitySet))

    @odata(name="grantedToIdentitiesV2")
    @property
    def granted_to_identities_v2(self) -> ClientValueCollection[SharePointIdentitySet]:
        """For link type permissions, the details of the users to whom permission was granted."""
        return self.properties.get("grantedToIdentitiesV2", ClientValueCollection(SharePointIdentitySet))

    @property
    def link(self) -> SharingLink:
        """Provides the link details of the current permission, if it is a link type permissions. Read-only."""
        return self.properties.get("link", SharingLink())

    @property
    def roles(self) -> StringCollection:
        """The type of permission, e.g. read. See below for the full list of roles. Read-only."""
        return self.properties.get("roles", StringCollection())

    @roles.setter
    def roles(self, value: List[str]) -> None:
        """Sets the type of permission

        Args:
            value (list[str]):
        """
        self.set_property("roles", StringCollection(value))

    @property
    def share_id(self) -> Optional[str]:
        """A unique token that can be used to access this shared item via the shares API. Read-only."""
        return self.properties.get("shareId", None)

    @property
    def has_password(self) -> Optional[bool]:
        """This indicates whether password is set for this permission, it's only showing in response.
        Optional and Read-only and for OneDrive Personal only.
        """
        return self.properties.get("hasPassword", None)

    @odata(name="inheritedFrom")
    @property
    def inherited_from(self) -> ItemReference:
        """
        If this content type is inherited from another scope (like a site),
        provides a reference to the item where the content type is defined.
        """
        return self.properties.get("inheritedFrom", ItemReference())

    @property
    def expiration_date_time(self) -> Optional[datetime]:
        """Gets the expirationDateTime property"""
        return self.properties.get("expirationDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Permission"
