from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.actions.download_file import DownloadFileQuery
from office365.sharepoint.actions.upload_file import UploadFileQuery
from office365.sharepoint.files.file import AbstractFile


class AttachmentFile(AbstractFile):
    """Represents an attachment file in a SharePoint List Item."""

    def download(self, file_object):
        """Download attachment file content

        :type file_object: typing.IO
        """

        def _download_inner():
            url = self.server_relative_url
            qry = DownloadFileQuery(self.context.web, url, file_object)
            self.context.add_query(qry)

        self.ensure_property("ServerRelativeUrl", _download_inner)

    def upload(self, file_object):
        """
        :type file_object: typing.IO
        """

        def _upload_inner():
            qry = UploadFileQuery(self.context.web, self.server_relative_url, file_object)
            self.context.add_query(qry)

        self.ensure_property("ServerRelativeUrl", _upload_inner)

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
            self._resource_path = ResourcePathServiceOperation(
                "GetFileByServerRelativeUrl", [value], ResourcePath("Web"))
