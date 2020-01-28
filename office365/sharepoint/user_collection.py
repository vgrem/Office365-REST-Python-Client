from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ClientQuery, ServiceOperationQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.utilities.http_method import HttpMethod
from office365.sharepoint.user import User


class UserCollection(ClientObjectCollection):
    """Represents a collection of User resources."""

    def __init__(self, context, resource_path=None):
        super(UserCollection, self).__init__(context, User, resource_path)

    def add_user(self, login_name):
        user = User(self.context)
        user._parent_collection = self
        user.set_property('LoginName', login_name)
        qry = ClientQuery(self.resourceUrl, HttpMethod.Post, user)
        self.context.add_query(qry, user)
        self.add_child(user)
        return user

    def get_by_email(self, email):
        """Retrieve User object by email"""
        return User(self.context, ResourcePathServiceOperation(self.context, self.resourcePath, "GetByEmail", [email]))

    def get_by_id(self, user_id):
        """Retrieve User object by id"""
        return User(self.context, ResourcePathServiceOperation(self.context, self.resourcePath, "GetById", [user_id]))

    def get_by_login_name(self, login_name):
        """Retrieve User object by login name"""
        return User(self.context,
                    ResourcePathServiceOperation(self.context, self.resourcePath, "GetByLoginName", [login_name]))

    def remove_by_id(self, _id):
        """Retrieve User object by id"""
        qry = ServiceOperationQuery(self, HttpMethod.Post, "RemoveById", [_id])
        self.context.add_query(qry)

    def remove_by_login_name(self, login_name):
        """Remove User object by login name"""
        qry = ServiceOperationQuery(self, HttpMethod.Post, "RemoveByLoginName", [login_name])
        self.context.add_query(qry)
