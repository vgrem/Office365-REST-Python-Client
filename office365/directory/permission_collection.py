from office365.directory.permission import Permission
from office365.entity_collection import EntityCollection


class PermissionCollection(EntityCollection):
    """Permission's collection"""

    def __init__(self, context, resource_path=None):
        super(PermissionCollection, self).__init__(context, Permission, resource_path)
