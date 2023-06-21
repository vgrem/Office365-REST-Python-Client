import os

from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.internal.queries.upload_session import create_upload_session_query_ex
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.files.file import File
from office365.sharepoint.files.creation_information import FileCreationInformation
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath


class FileCollection(BaseEntityCollection):
    """Represents a collection of File resources."""

    def __init__(self, context, resource_path=None, parent=None):
        super(FileCollection, self).__init__(context, File, resource_path, parent)

    def upload(self, path_or_file):
        """Uploads a file into folder.

        Note: This method only supports files up to 4MB in size!
        Consider create_upload_session method instead for larger files

        :param str or typing.IO path_or_file: path where file to upload resides or file handle
        """
        if hasattr(path_or_file, 'read'):
            content = path_or_file.read()
            name = os.path.basename(path_or_file.name)
            return self.add(name, content, True)
        else:
            with open(path_or_file, 'rb') as f:
                content = f.read()
            name = os.path.basename(path_or_file)
            return self.add(name, content, True)

    def create_upload_session(self, path_or_file, chunk_size, chunk_uploaded=None, **kwargs):
        """Upload a file as multiple chunks

        :param str or typing.IO path_or_file: path where file to upload resides or file handle
        :param int chunk_size: upload chunk size (in bytes)
        :param (long)->None or None chunk_uploaded: uploaded event
        :param kwargs: arguments to pass to chunk_uploaded function
        """

        qry = create_upload_session_query_ex(self, path_or_file, chunk_size, chunk_uploaded, **kwargs)
        self.context.add_query(qry)
        return qry.return_type

    def add(self, url, content, overwrite=False):
        """
        Adds a file to the collection based on provided file creation information. A reference to the SP.File that
        was added is returned.

        :param str url: Specifies the URL of the file to be added. It MUST NOT be NULL. It MUST be a URL of relative
            or absolute form. Its length MUST be equal to or greater than 1.
        :param bool overwrite: Specifies whether to overwrite an existing file with the same name and in the same
            location as the one being added.
        :param str or bytes content: Specifies the binary content of the file to be added.
        """
        return_type = File(self.context)
        self.add_child(return_type)
        params = FileCreationInformation(url=url, overwrite=overwrite)
        qry = ServiceOperationQuery(self, "add", params.to_json(), content, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_template_file(self, url_of_file, template_file_type):
        """Adds a ghosted file to an existing list or document library.

        :param int template_file_type: refer TemplateFileType enum
        :param str url_of_file: server relative url of a file
        """
        return_type = File(self.context)
        self.add_child(return_type)

        def _parent_folder_loaded():
            params = {
                "urlOfFile": str(SPResPath.create_relative(self.parent.properties["ServerRelativeUrl"], url_of_file)),
                "templateFileType": template_file_type
            }
            qry = ServiceOperationQuery(self, "addTemplateFile", params, None, None, return_type)
            self.context.add_query(qry)

        self.parent.ensure_property("ServerRelativeUrl", _parent_folder_loaded)
        return return_type

    def get_by_url(self, url):
        """Retrieve File object by url"""
        return File(self.context, ServiceOperationPath("GetByUrl", [url], self.resource_path))

    def get_by_id(self, _id):
        """Gets the File with the specified ID."""
        return File(self.context, ServiceOperationPath("getById", [_id], self.resource_path))
