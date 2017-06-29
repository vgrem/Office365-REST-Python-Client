from office365.runtime.action_type import ActionType
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ClientQuery
from office365.sharepoint.file import File


class FileCollection(ClientObjectCollection):
    """Represents a collection of File resources."""

    def add(self, file_creation_information):
        """Creates a File resource"""
        file_new = File(self.context)
        qry = ClientQuery.service_operation_query(self,
                                                  ActionType.PostMethod,
                                                  "add",
                                                  {
                                                      "overwrite": file_creation_information.overwrite,
                                                      "url": file_creation_information.url
                                                  },
                                                  file_creation_information.content)
        self.context.add_query(qry, file_new)
        self.add_child(file_new)
        return file_new
