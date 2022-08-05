import os

from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.internal.queries.create_file import create_file_query
from office365.sharepoint.internal.queries.upload_session import create_upload_session_query
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.files.file import File
from office365.sharepoint.files.creation_information import FileCreationInformation


class FileCollection(BaseEntityCollection):
    """Represents a collection of File resources."""

    def __init__(self, context, resource_path=None):
        super(FileCollection, self).__init__(context, File, resource_path)

    def upload(self, file_name, content):
        """Uploads a file into folder

        :type file_name: str
        :type content: bytes or str
        :rtype: office365.sharepoint.files.file.File
        """
        info = FileCreationInformation(url=file_name, overwrite=True, content=content)
        qry = create_file_query(self, info)
        self.context.add_query(qry)
        return qry.return_type

    def create_upload_session(self, source_path, chunk_size, chunk_uploaded=None, **kwargs):
        """Upload a file as multiple chunks

        :param str source_path: path where file to upload resides
        :param int chunk_size: upload chunk size (in bytes)
        :param (long)->None or None chunk_uploaded: uploaded event
        :param kwargs: arguments to pass to chunk_uploaded function
        """
        file_size = os.path.getsize(source_path)
        if file_size > chunk_size:
            qry = create_upload_session_query(self, source_path, chunk_size, chunk_uploaded, **kwargs)
            self.context.add_query(qry)
            return qry.return_type
        else:
            with open(source_path, 'rb') as content_file:
                file_content = content_file.read()
            return self.upload(os.path.basename(source_path), file_content)

    def add(self, file_creation_information):
        """Creates a File resource

        :type file_creation_information: office365.sharepoint.files.creation_information.FileCreationInformation
        :rtype: office365.sharepoint.files.file.File
        """
        qry = create_file_query(self, file_creation_information)
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
        return File(self.context, ServiceOperationPath("GetByUrl", [url], self.resource_path))

    def get_by_id(self, _id):
        """Gets the File with the specified ID."""
        return File(self.context, ServiceOperationPath("getById", [_id], self.resource_path))
