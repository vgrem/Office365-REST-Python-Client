from office365.entity_collection import EntityCollection
from office365.onedrive.permissions.permission import Permission


class PermissionCollection(EntityCollection):
    """Drive list's collection"""

    def __init__(self, context, resource_path=None):
        super(PermissionCollection, self).__init__(context, Permission, resource_path)
