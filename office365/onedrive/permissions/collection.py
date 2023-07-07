from office365.directory.permissions.identity import Identity
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.permissions.permission import Permission
from office365.runtime.queries.create_entity import CreateEntityQuery


class PermissionCollection(EntityCollection):
    """Drive list's collection"""

    def __init__(self, context, resource_path=None):
        super(PermissionCollection, self).__init__(context, Permission, resource_path)

    def add(self, roles, identity=None, identity_type=None):
        """
        Create a new permission object.

        :param list[str] roles: Permission types
        :param Application or User or Device or User or Group or str identity: Identity object or identifier
        :param str identity_type: Identity type
        """

        return_type = Permission(self.context)

        known_identities = {
            "application": self.context.applications,
            "user": self.context.users,
            "device": self.context.device_app_management,
            "group": self.context.groups
        }

        if isinstance(identity, Entity):
            identity_type = type(identity).__name__.lower()
        else:
            if identity_type is None:
                raise ValueError("Identity type is a mandatory when identity identifier is specified")
            known_identity = known_identities.get(identity_type, None)
            if known_identity is None:
                raise ValueError("Unknown identity type")
            identity = known_identity[identity]

        def _create():
            payload = {
                "roles": roles,
                "grantedToIdentities": [{
                    identity_type: Identity(display_name=identity.display_name, _id=identity.id)
                }]
            }

            self.add_child(return_type)
            qry = CreateEntityQuery(self, payload, return_type)
            self.context.add_query(qry)
        identity.ensure_properties(["displayName"], _create)
        return return_type

    def delete_all(self):
        """
        Remove all access to resource
        """
        def _after_loaded(return_type):
            for permission in return_type:  # type: Permission
                permission.delete_object()
        self.context.load(self, after_loaded=_after_loaded)
        return self
