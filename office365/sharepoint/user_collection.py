from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.user import User


class UserCollection(ClientObjectCollection):
    """Represents a collection of User resources."""

    def get_by_email(self, email):
        """Retrieve User object by email"""
        return User(self.context, ResourcePathServiceOperation(self.context, self.resource_path, "GetByEmail", [email]))

    def get_by_id(self, user_id):
        """Retrieve User object by id"""
        return User(self.context, ResourcePathServiceOperation(self.context, self.resource_path, "GetById", [user_id]))

    def get_by_login_name(self, login_name):
        """Retrieve User object by login name"""
        return User(self.context,
                    ResourcePathServiceOperation(self.context, self.resource_path, "GetByLoginName", [login_name]))

    def remove_by_id(self, id):
        """Retrieve User object by id"""
        return User(self.context, ResourcePathServiceOperation(self.context, self.resource_path, "RemoveById", [id]))

    def remove_by_login_name(self, login_name):
        """Remove User object by login name"""
        return User(self.context,
                    ResourcePathServiceOperation(self.context, self.resource_path, "RemoveByLoginName", [login_name]))
