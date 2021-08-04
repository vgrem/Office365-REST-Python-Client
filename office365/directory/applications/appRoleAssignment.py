from office365.directory.directory_object import DirectoryObject
from office365.entity_collection import EntityCollection


class AppRoleAssignment(DirectoryObject):
    pass


class AppRoleAssignmentCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(AppRoleAssignmentCollection, self).__init__(context, AppRoleAssignment, resource_path)
