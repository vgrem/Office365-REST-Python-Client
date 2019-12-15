from office365.directory.group import Group
from office365.directory.directory_object_collection import DirectoryObjectCollection


class GroupCollection(DirectoryObjectCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super(GroupCollection, self).__init__(context, Group, resource_path)
