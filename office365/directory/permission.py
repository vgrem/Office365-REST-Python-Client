from office365.directory.identitySet import IdentitySet
from office365.entity import Entity
from office365.onedrive.sharingInvitation import SharingInvitation
from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.queries.update_entity_query import UpdateEntityQuery


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
        return self.properties.get('roles', [])

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
