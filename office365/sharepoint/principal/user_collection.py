from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.principal.user import User


class UserCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        """Represents a collection of User resources."""
        super(UserCollection, self).__init__(context, User, resource_path)

    def add_user(self, login_name):
        """
        Creates a user

        :type login_name: str
        """
        return_type = User(self.context)
        self.add_child(return_type)
        return_type.set_property('LoginName', login_name)
        qry = CreateEntityQuery(self, return_type, return_type)
        self.context.add_query(qry)
        return return_type

    def get_by_email(self, email):
        """Retrieve User object by email

        :type email: str
        """
        return User(self.context, ServiceOperationPath("GetByEmail", [email], self.resource_path))

    def get_by_id(self, user_id):
        """Retrieve User object by id"""
        return User(self.context, ServiceOperationPath("GetById", [user_id], self.resource_path))

    def get_by_login_name(self, login_name):
        """Retrieve User object by login name

        :type login_name: str
        """
        return User(self.context, ServiceOperationPath("GetByLoginName", [login_name], self.resource_path))

    def remove_by_id(self, _id):
        """Retrieve User object by id"""
        qry = ServiceOperationQuery(self, "RemoveById", [_id])
        self.context.add_query(qry)
        return self

    def remove_by_login_name(self, login_name):
        """Remove User object by login name

        :param str login_name:
        """
        qry = ServiceOperationQuery(self, "RemoveByLoginName", [login_name])
        self.context.add_query(qry)
        return self
