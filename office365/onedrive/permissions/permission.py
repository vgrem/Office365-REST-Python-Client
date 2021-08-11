from office365.directory.identities.identity_set import IdentitySet
from office365.entity import Entity
from office365.onedrive.listitems.item_reference import ItemReference
from office365.onedrive.permissions.sharing_invitation import SharingInvitation
from office365.runtime.client_value_collection import ClientValueCollection


class Permission(Entity):
    """The Permission resource provides information about a sharing permission granted for a DriveItem resource."""

    @property
    def invitation(self):
        """For user type permissions, the details of the users & applications for this permission."""
        return self.properties.get('invitation', SharingInvitation())

    @property
    def granted_to(self):
        """For user type permissions, the details of the users & applications for this permission."""
        return self.properties.get('grantedTo', IdentitySet())

    @property
    def roles(self):
        """The type of permission, e.g. read. See below for the full list of roles. Read-only."""
        return self.properties.get('roles', ClientValueCollection(str))

    @property
    def share_id(self):
        """A unique token that can be used to access this shared item via the shares API. Read-only.

        :rtype: str
        """
        return self.properties.get('shareId', None)

    @property
    def has_password(self):
        """This indicates whether password is set for this permission, it's only showing in response.
        Optional and Read-only and for OneDrive Personal only.

        :rtype: bool
        """
        return self.properties.get('hasPassword', None)

    @property
    def inherited_from(self):
        """
        If this content type is inherited from another scope (like a site),
        provides a reference to the item where the content type is defined.
        """
        return self.properties.get("inheritedFrom", ItemReference())
