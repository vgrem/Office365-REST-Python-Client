from office365.entity_collection import EntityCollection
from office365.onedrive.permissions.permission import Permission


class PermissionCollection(EntityCollection):
    """Drive list's collection"""

    def __init__(self, context, resource_path=None):
        super(PermissionCollection, self).__init__(context, Permission, resource_path)

    def delete_all(self):
        """
        Remove all access to resource
        """
        def _after_loaded(return_type):
            for permission in return_type:  # type: Permission
                permission.delete_object()
        self.context.load(self, after_loaded=_after_loaded)
        return self
