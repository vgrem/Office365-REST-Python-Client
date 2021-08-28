from office365.onedrive.internal.queries.upload_session_query import UploadSessionQuery
from office365.outlook.mail.attachment_item import AttachmentItem
from office365.outlook.mail.attachment_type import AttachmentType


class AttachmentUploadQuery(UploadSessionQuery):
    """Create an upload session to allow your app to upload attachments up to the maximum file size. An upload session
    allows your app to upload ranges of the file in sequential API requests, which allows the transfer to be resumed
    if a connection is dropped while the upload is in progress. """

    def create_upload_session(self):
        attachment_item = AttachmentItem(attachment_type=AttachmentType.file, name=self.file_name, size=self.file_size)
        return self.binding_type.create_upload_session(attachment_item)
