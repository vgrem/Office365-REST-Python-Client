from office365.directory.applications.roles.assignment import AppRoleAssignment
from office365.entity_collection import EntityCollection


class AppRoleAssignmentCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(AppRoleAssignmentCollection, self).__init__(context, AppRoleAssignment, resource_path)
