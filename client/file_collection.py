from client.client_object_collection import ClientObjectCollection
from client.file import File
from client.runtime.client_query import ClientQuery


class FileCollection(ClientObjectCollection):
    """Represents a collection of File resources."""

    def add(self, file_creation_information):
        """Creates a File resource"""
        file_new = File(self.context)
        payload = file_creation_information
        qry = ClientQuery.create_create_query(file_new, self.url, payload)
        self.context.add_query(qry)
        self.add_child(file)
        return file
