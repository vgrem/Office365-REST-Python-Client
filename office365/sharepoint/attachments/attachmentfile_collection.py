from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.queries.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.attachments.attachmentfile import AttachmentFile
from office365.sharepoint.attachments.attachmentfile_creation_information import AttachmentfileCreationInformation
from office365.sharepoint.files.file import File


class AttachmentFileCollection(ClientObjectCollection):
    """Represents a collection of AttachmentFile resources."""

    def __init__(self, context, resource_path=None):
        super(AttachmentFileCollection, self).__init__(context, AttachmentFile, resource_path)

    def add(self, attachment_file_information):
        """Creates an attachment"""
        if isinstance(attachment_file_information, dict):
            attachment_file_information = AttachmentfileCreationInformation(
                attachment_file_information.get('filename'),
                attachment_file_information.get('content')
            )

        target_file = File(self.context)
        self.add_child(target_file)
        qry = ServiceOperationQuery(self,
                                    "add",
                                    {
                                        "filename": attachment_file_information.filename,
                                    },
                                    attachment_file_information.content,
                                    None,
                                    target_file)
        self.context.add_query(qry)
        return target_file

    def get_by_filename(self, filename):
        """Retrieve Attachment file object by filename"""
        return AttachmentFile(self.context,
                              ResourcePathServiceOperation("GetByFileName", [filename], self.resource_path))
