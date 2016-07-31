from client.office365.runtime.client_object_collection import ClientObjectCollection
from client.office365.runtime.client_query import ClientQuery
from client.office365.sharepoint.file import File


class FileCollection(ClientObjectCollection):
    """Represents a collection of File resources."""

    def add(self, file_creation_information):
        """Creates a File resource"""
        file_new = File(self.context)
        payload = file_creation_information
        qry = ClientQuery.create_entry_query(self, payload)
        self.context.add_query(qry, file_new)
        self.add_child(file)
        return file
