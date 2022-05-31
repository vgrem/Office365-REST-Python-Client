from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.directory.group import Group


class GroupAndUserStatus(BaseEntity):

    @property
    def group(self):
        """Get a Group"""
        return self.properties.get("Group",
                                   Group(self.context, ResourcePath("Group", self.resource_path)))
