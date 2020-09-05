from office365.graph.directory.identitySet import IdentitySet
from office365.sharepoint.base_entity import BaseEntity


class ChangeTrackedEntity(BaseEntity):

    @property
    def created_datetime(self):
        return self.properties.get('createdDateTime', None)

    @property
    def last_modified_datetime(self):
        return self.properties.get('lastModifiedDateTime', None)

    @property
    def last_modified_by(self):
        return self.properties.get('lastModifiedBy', IdentitySet())
