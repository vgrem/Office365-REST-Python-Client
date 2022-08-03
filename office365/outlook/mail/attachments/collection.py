import base64

from office365.entity_collection import EntityCollection
from office365.outlook.internal.queries.attachment_upload import AttachmentUploadQuery
from office365.outlook.mail.attachments.attachment import Attachment
from office365.onedrive.upload_session import UploadSession
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery


class AttachmentCollection(EntityCollection):
    """Attachment collection"""

    def __init__(self, context, resource_path=None):
        super(AttachmentCollection, self).__init__(context, Attachment, resource_path)

    def add_file(self, name, content, content_type=None):
        """
        Attach a file to message

        :param str name: The name representing the text that is displayed below the icon representing the
             embedded attachment
        :param str content: The contents of the file
        :param str or None content_type: The content type of the attachment.
        """
        from office365.outlook.mail.attachments.file import FileAttachment
        return_type = FileAttachment(self.context)
        return_type.name = name
        return_type.content_bytes = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        return_type.content_type = content_type
        self.add_child(return_type)
        return self

    def resumable_upload(self, source_path, chunk_size=1000000):
        """
        Create an upload session to allow your app to upload files up to the maximum file size.
        An upload session allows your app to upload ranges of the file in sequential API requests,
        which allows the transfer to be resumed if a connection is dropped while the upload is in progress.

        :param str source_path: Local file path
        :param int chunk_size: chunk size
        """
        upload_query = AttachmentUploadQuery(self, source_path, chunk_size, None)
        self.context.add_query(upload_query)
        return upload_query.return_type

    def create_upload_session(self, attachment_item):
        """
        Create an upload session that allows an app to iteratively upload ranges of a file,
             so as to attach the file to the specified Outlook item. The item can be a message or event.

        :type attachment_item: office365.mail.attachment_item.AttachmentItem
        """
        return_type = ClientResult(self.context, UploadSession())
        payload = {"AttachmentItem": attachment_item}
        qry = ServiceOperationQuery(self, "createUploadSession", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type
