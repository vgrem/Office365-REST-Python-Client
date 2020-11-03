from office365.runtime.client_object import ClientObject
from office365.runtime.queries.update_entity_query import UpdateEntityQuery


class BaseEntity(ClientObject):

    def __init__(self, context, resource_path=None, namespace="SP", parent_collection=None):
        """
        SharePoint entity

        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param ResourcePath resource_path: Resource Path
        :param str namespace:  default namespace
        """
        super().__init__(context, resource_path, None, parent_collection)
        self._namespace = namespace

    def with_credentials(self, credentials):
        self.context.with_credentials(credentials)
        return self

    def update(self):
        """Updates the resource."""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)
        return self

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
