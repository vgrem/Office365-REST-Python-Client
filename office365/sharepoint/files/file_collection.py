from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.queries.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.files.file import File
from office365.sharepoint.actions.create_file import CreateFileQuery
from office365.sharepoint.actions.upload_session import UploadSessionQuery


class FileCollection(ClientObjectCollection):
    """Represents a collection of File resources."""

    def __init__(self, context, resource_path=None):
        super(FileCollection, self).__init__(context, File, resource_path)

    def create_upload_session(self, source_path, chunk_size, chunk_uploaded=None):
        """Upload a file as multiple chunks

        :param str source_path: path where file to upload resides
        :param int chunk_size: upload chunk size
        :param (long)->None or None chunk_uploaded: uploaded event
        :rtype: office365.sharepoint.file.File
        """
        qry = UploadSessionQuery(self, source_path, chunk_size, chunk_uploaded)
        self.context.add_query(qry)
        return qry.return_type

    def add(self, file_creation_information):
        """Creates a File resource

        :type file_creation_information: office365.sharepoint.file_creation_information.FileCreationInformation
        """
        qry = CreateFileQuery(self, file_creation_information)
        self.context.add_query(qry)
        return qry.return_type

    def add_template_file(self, url_of_file, template_file_type):
        """Adds a ghosted file to an existing list or document library.

        :param int template_file_type: refer TemplateFileType enum
        :param str url_of_file: server relative url of a file
        """
        target_file = File(self.context)
        self.add_child(target_file)
        qry = ServiceOperationQuery(self,
                                    "addTemplateFile",
                                    {
                                        "urlOfFile": url_of_file,
                                        "templateFileType": template_file_type
                                    }, None, None, target_file)
        self.context.add_query(qry)
        return target_file

    def get_by_url(self, url):
        """Retrieve File object by url"""
        return File(self.context, ResourcePathServiceOperation("GetByUrl", [url], self.resource_path))

    def get_by_id(self, _id):
        """Gets the File with the specified ID."""
        return File(self.context, ResourcePathServiceOperation("getById", [_id], self.resource_path))
