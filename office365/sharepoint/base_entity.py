from office365.runtime.client_object import ClientObject
from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.queries.update_entity_query import UpdateEntityQuery


class BaseEntity(ClientObject):

    def __init__(self, context, resource_path=None, namespace="SP", parent_collection=None):
        """
        SharePoint specific entity

        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param office365.runtime.client_path.ClientPath resource_path: Resource Path
        :param str namespace: default namespace
        """
        super(BaseEntity, self).__init__(context, resource_path, parent_collection, namespace)

    def with_credentials(self, credentials):
        """
        :type credentials:  UserCredential or ClientCredential
        """
        self.context.with_credentials(credentials)
        return self

    def delete_object(self):
        """The recommended way to delete a SharePoint entity"""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
        return self

    def update(self, *args):
        """The recommended way to update a SharePoint entity"""
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

