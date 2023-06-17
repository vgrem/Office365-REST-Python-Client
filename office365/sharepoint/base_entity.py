from office365.runtime.client_object import ClientObject
from office365.runtime.queries.delete_entity import DeleteEntityQuery
from office365.runtime.queries.update_entity import UpdateEntityQuery


class BaseEntity(ClientObject):
    """SharePoint specific entity"""

    def with_credentials(self, credentials):
        """
        :type self: T
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
            self._entity_type_name = ".".join(["SP", type(self).__name__])
        return self._entity_type_name

    @property
    def property_ref_name(self):
        return "Id"
