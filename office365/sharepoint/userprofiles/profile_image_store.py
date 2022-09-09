from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class ProfileImageStore(BaseEntity):
    """The ProfileImageStore class specifies the user profile and service context."""

    def __init__(self, context):
        super(ProfileImageStore, self).__init__(context, ResourcePath("SP.UserProfiles.ProfileImageStore"))

    @property
    def entity_type_name(self):
        return "SP.UserProfiles.ProfileImageStore"
