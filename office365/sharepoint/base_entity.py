from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import UpdateEntityQuery


class BaseEntity(ClientObject):

    def __init__(self, context, resource_path=None, namespace="SP"):
        """
        SharePoint base entity

        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param ResourcePath resource_path:
        :param str namespace:
        """
        super().__init__(context, resource_path)
        self._namespace = namespace

    def with_credentials(self, credentials):
        self.context.with_credentials(credentials)
        return self

    def execute_query(self):
        self.context.execute_query()
        return self

    def load(self):
        self.context.load(self)
        return self

    def update(self):
        """Updates the resource."""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    @property
    def context(self):
        """
        :rtype: office365.sharepoint.client_context.ClientContext
        """
        return self._context

    @property
    def entity_type_name(self):
        if self._entity_type_name is None:
            self._entity_type_name = ".".join([self._namespace, type(self).__name__])
        return self._entity_type_name
