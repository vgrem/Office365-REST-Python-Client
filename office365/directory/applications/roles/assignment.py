from office365.directory.object import DirectoryObject
from office365.entity_collection import EntityCollection


class AppRoleAssignment(DirectoryObject):
    """
    Used to record when a user, group, or service principal is assigned an app role for an app.

    An app role assignment is a relationship between the assigned principal (a user, a group, or a service principal),
    a resource application (the app's service principal) and an app role defined on the resource application.
    """
    pass


class AppRoleAssignmentCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(AppRoleAssignmentCollection, self).__init__(context, AppRoleAssignment, resource_path)
