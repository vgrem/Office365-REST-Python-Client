from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.directory.user import User


class DirectorySession(BaseEntity):
    def __init__(self, context):
        super(DirectorySession, self).__init__(context, ResourcePath("SP.Directory.DirectorySession"))

    def me(self):
        """Create a modern site"""
        user = User(self.context, ResourcePath("me", self.resource_path))
        qry = ServiceOperationQuery(self, "me", None, None, None, user)
        self.context.add_query(qry)
        return user
