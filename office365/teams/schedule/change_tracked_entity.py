from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity


class ChangeTrackedEntity(Entity):
    """Represents an entity to track changes made to any supported schedule and associated resource."""

    @property
    def created_datetime(self):
        """
        The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time.
        For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
        """
        return self.properties.get('createdDateTime', None)

    @property
    def last_modified_datetime(self):
        """
        The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time.
        For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
        """
        return self.properties.get('lastModifiedDateTime', None)

    @property
    def last_modified_by(self):
        """Identity of the person who last modified the entity."""
        return self.properties.get('lastModifiedBy', IdentitySet())
