from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.attachments.attachmentfile import AttachmentFile
from office365.sharepoint.attachments.attachmentfile_creation_information import AttachmentfileCreationInformation
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.files.file import File


class AttachmentFileCollection(BaseEntityCollection):
    """Represents a collection of AttachmentFile resources."""

    def __init__(self, context, resource_path=None):
        super(AttachmentFileCollection, self).__init__(context, AttachmentFile, resource_path)

    def get(self):
        """
        :rtype: AttachmentFileCollection
        """
        return super(AttachmentFileCollection, self).get()

    def add(self, attachment_file_information):
        """
        Creates an attachment
        :type attachment_file_information: AttachmentfileCreationInformation
        """
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

    def add_using_path(self):
        pass

    def get_by_filename(self, filename):
        """Retrieve Attachment file object by filename

        :type filename: str
        """
        return AttachmentFile(context=self.context,
                              resource_path=ServiceOperationPath("GetByFileName", [filename],
                                                                 self.resource_path),
                              parent_collection=self)
