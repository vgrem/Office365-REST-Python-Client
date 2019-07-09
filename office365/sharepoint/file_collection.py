from office365.runtime.action_type import ActionType
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ClientQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.file import File


class FileCollection(ClientObjectCollection):
    """Represents a collection of File resources."""

    # The object type this collection holds
    item_type = File

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

    def add_template_file(self, url_of_file, template_file_type):
        """Adds a ghosted file to an existing list or document library."""
        file_new = File(self.context)
        qry = ClientQuery.service_operation_query(self,
                                                  ActionType.PostMethod,
                                                  "addTemplateFile",
                                                  {
                                                      "urlOfFile": url_of_file,
                                                      "templateFileType": template_file_type
                                                  })
        self.context.add_query(qry, file_new)
        self.add_child(file_new)
        return file_new

    def get_by_url(self, url):
        """Retrieve File object by url"""
        return File(self.context, ResourcePathServiceOperation(self.context, self.resource_path, "GetByUrl", [url]))
