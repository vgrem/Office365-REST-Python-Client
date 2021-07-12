import os

from office365.entity_collection import EntityCollection
from office365.mail.attachment import Attachment
from office365.mail.attachment_item import AttachmentItem
from office365.mail.attachment_type import AttachmentType
from office365.onedrive.uploadSession import UploadSession
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


class AttachmentCollection(EntityCollection):
    """Attachment collection"""

    def __init__(self, context, resource_path=None):
        super(AttachmentCollection, self).__init__(context, Attachment, resource_path)

    def resumable_upload(self, source_path, chunk_size=1000000):
        """
        Create an upload session to allow your app to upload files up to the maximum file size.
        An upload session allows your app to upload ranges of the file in sequential API requests,
        which allows the transfer to be resumed if a connection is dropped while the upload is in progress.

        :param str source_path: Local file path
        :param int chunk_size: chunk size
        """
        file_size = os.path.getsize(source_path)
        file_name = os.path.basename(source_path)
        attachment_item = AttachmentItem(attachmentType=AttachmentType.file, name=file_name, size=file_size)
        #upload_session = self.create_upload_session(attachment_item)
        #upload_query = ResumableFileUpload(self, source_path, chunk_size)
        #self.context.add_query(upload_query)
        #return upload_query.return_type

    def create_upload_session(self, attachment_item):
        """
        Create an upload session that allows an app to iteratively upload ranges of a file,
        so as to attach the file to the specified Outlook item. The item can be a message or event.
        :type attachment_item: office365.mail.attachment_item.AttachmentItem
        """
        result = ClientResult(self.context, UploadSession())
        qry = ServiceOperationQuery(self,
                                    "createUploadSession",
                                    None,
                                    {
                                        "AttachmentItem": attachment_item
                                    },
                                    None,
                                    result
                                    )
        self.context.add_query(qry)
        return result
