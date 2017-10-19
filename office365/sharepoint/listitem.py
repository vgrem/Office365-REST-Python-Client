from office365.runtime.client_query import ClientQuery
from office365.sharepoint.securable_object import SecurableObject


class ListItem(SecurableObject):
    """ListItem client object resource"""

    def update(self):
        """Update the list."""
        qry = ClientQuery.update_entry_query(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the list."""
        qry = ClientQuery.delete_entry_query(self)
        self.context.add_query(qry)
