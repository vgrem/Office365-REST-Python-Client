from office365.graph.directory.permission import Permission
from office365.runtime.client_object_collection import ClientObjectCollection


class PermissionCollection(ClientObjectCollection):
    """Permission's collection"""

    def __init__(self, context, resource_path=None):
        super(PermissionCollection, self).__init__(context, Permission, resource_path)
