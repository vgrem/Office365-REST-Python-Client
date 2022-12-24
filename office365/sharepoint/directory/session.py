from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.directory.user import User


class DirectorySession(BaseEntity):

    def __init__(self, context):
        super(DirectorySession, self).__init__(context, ResourcePath("SP.Directory.DirectorySession"))

    @property
    def me(self):
        return self.properties.get('Me', User(self.context, ResourcePath("Me", self.resource_path)))

    def get_graph_user(self, principal_name):
        """
        :type principal_name: str
        """
        user = User(self.context)
        qry = ServiceOperationQuery(self, "GetGraphUser", [principal_name], None, None, user)
        self.context.add_query(qry)
        return user

    @property
    def entity_type_name(self):
        return "SP.Directory.DirectorySession"
