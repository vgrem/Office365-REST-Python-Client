from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import CreateEntityQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.user import User


class UserCollection(ClientObjectCollection):
    """Represents a collection of User resources."""

    def __init__(self, context, resource_path=None):
        super(UserCollection, self).__init__(context, User, resource_path)

    def add_user(self, login_name):
        user = User(self.context)
        user._parent_collection = self
        user.set_property('LoginName', login_name)
        qry = CreateEntityQuery(self, user, user)
        self.context.add_query(qry)
        self.add_child(user)
        return user

    def get_by_email(self, email):
        """Retrieve User object by email"""
        return User(self.context, ResourcePathServiceOperation("GetByEmail", [email], self.resource_path))

    def get_by_id(self, user_id):
        """Retrieve User object by id"""
        return User(self.context, ResourcePathServiceOperation("GetById", [user_id], self.resource_path))

    def get_by_login_name(self, login_name):
        """Retrieve User object by login name"""
        return User(self.context,
                    ResourcePathServiceOperation("GetByLoginName", [login_name], self.resource_path))

    def remove_by_id(self, _id):
        """Retrieve User object by id"""
        qry = ServiceOperationQuery(self, "RemoveById", [_id])
        self.context.add_query(qry)

    def remove_by_login_name(self, login_name):
        """Remove User object by login name"""
        qry = ServiceOperationQuery(self, "RemoveByLoginName", [login_name])
        self.context.add_query(qry)
