from office365.entity import Entity
from office365.entity_collection import EntityCollection


class LicenseDetails(Entity):
    """Contains information about a license assigned to a user."""
    pass


class LicenseDetailsCollection(EntityCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super(LicenseDetailsCollection, self).__init__(context, LicenseDetails, resource_path)
