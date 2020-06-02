from office365.graph.directory.identitySet import IdentitySet
from office365.graph.entity import Entity


class Permission(Entity):
    """The Permission resource provides information about a sharing permission granted for a DriveItem resource."""

    @property
    def grantedTo(self):
        """For user type permissions, the details of the users & applications for this permission."""
        if self.is_property_available('drive'):
            return self.properties['drive']
        else:
            return IdentitySet()
