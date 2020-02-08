from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ServiceOperationQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.file import File
from office365.sharepoint.upload_session import UploadSession


class FileCollection(ClientObjectCollection):
    """Represents a collection of File resources."""

    def __init__(self, context, resource_path=None):
        super(FileCollection, self).__init__(context, File, resource_path)

    def create_upload_session(self, source_path, chunk_size, chunk_uploaded=None):
        """Upload a file as multiple chunks"""
        session = UploadSession(source_path, chunk_size, chunk_uploaded)
        session.build_query(self)
        return session.file

    def add(self, file_creation_information):
        """Creates a File resource"""
        file_new = File(self.context)
        qry = ServiceOperationQuery(self,
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
        qry = ServiceOperationQuery(self,
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
        return File(self.context, ResourcePathServiceOperation("GetByUrl", [url], self.resourcePath))

    def get_by_id(self, _id):
        """Gets the File with the specified ID."""
        return File(self.context, ResourcePathServiceOperation("getById", [_id], self.resourcePath))
