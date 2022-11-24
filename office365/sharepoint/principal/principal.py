from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity import BaseEntity


class Principal(BaseEntity):
    """Represents a user or group that can be assigned permissions to control security."""

    @property
    def id(self):
        """Gets a value that specifies the member identifier for the user or group.

        :rtype: int or None
        """
        return self.properties.get('Id', None)

    @property
    def title(self):
        """Gets a value that specifies the name of the principal.

        :rtype: str or None
        """
        return self.properties.get('Title', None)

    @title.setter
    def title(self, value):
        """
        Sets a value that specifies the name of the principal.

        :type value: str
        """
        self.set_property('Title', value)

    @property
    def login_name(self):
        """Gets the login name of the principal.

        :rtype: str or None
        """
        return self.properties.get('LoginName', None)

    @property
    def user_principal_name(self):
        """Gets the UPN of the principal.

        :rtype: str or None
        """
        return self.properties.get('UserPrincipalName', None)

    @property
    def is_hidden_in_ui(self):
        """Gets the login name of the principal.

        :rtype: bool or None
        """
        return self.properties.get('IsHiddenInUI', None)

    @property
    def principal_type(self):
        """Gets the type of the principal.

        :rtype: int or None
        """
        return self.properties.get('PrincipalType', None)

    def set_property(self, name, value, persist_changes=True):
        super(Principal, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id":
                self._resource_path = ServiceOperationPath("GetById", [value], self.parent_collection.resource_path)
            elif name == "LoginName":
                self._resource_path = ServiceOperationPath("GetByName", [value], self.parent_collection.resource_path)
        return self
