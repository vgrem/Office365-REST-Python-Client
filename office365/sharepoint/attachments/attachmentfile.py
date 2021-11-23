from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.internal.queries.download_file import create_download_file_query
from office365.sharepoint.internal.queries.upload_file import create_upload_file_query
from office365.sharepoint.files.file import AbstractFile


class AttachmentFile(AbstractFile):
    """Represents an attachment file in a SharePoint List Item."""

    def download(self, file_object):
        """Download attachment file content

        :type file_object: typing.IO
        """

        def _download_file():
            source_file = self.context.web.get_file_by_server_relative_path(self.server_relative_url)
            qry = create_download_file_query(source_file, file_object)
            self.context.add_query(qry)

        self.ensure_property("ServerRelativeUrl", _download_file)
        return self

    def upload(self, file_object):
        """
        :type file_object: typing.IO
        """

        def _upload_file():
            target_file = self.context.web.get_file_by_server_relative_url(self.server_relative_url)
            qry = create_upload_file_query(target_file, file_object)
            self.context.add_query(qry)

        self.ensure_property("ServerRelativeUrl", _upload_file)
        return self

    @property
    def file_name(self):
        """
        :rtype: str or None
        """
        return self.properties.get("FileName", None)

    @property
    def server_relative_url(self):
        """
        :rtype: str or None
        """
        return self.properties.get("ServerRelativeUrl", None)

    @property
    def parent_collection(self):
        """
        :rtype: office365.sharepoint.attachments.attachmentfile_collection.AttachmentFileCollection
        """
        return self._parent_collection

    def set_property(self, name, value, persist_changes=True):
        super(AttachmentFile, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path

        if name == "ServerRelativeUrl":
            self._resource_path = ServiceOperationPath(
                "getFileByServerRelativeUrl", [value], ResourcePath("Web"))
