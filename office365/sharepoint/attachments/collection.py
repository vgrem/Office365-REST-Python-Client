from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.attachments.attachment import Attachment
from office365.sharepoint.attachments.creation_information import AttachmentCreationInformation
from office365.sharepoint.base_entity_collection import BaseEntityCollection


class AttachmentCollection(BaseEntityCollection):
    """Represents a collection of Attachment resources."""

    def __init__(self, context, resource_path=None, parent=None):
        super(AttachmentCollection, self).__init__(context, Attachment, resource_path, parent)

    def add(self, attachment_file_information):
        """
        Adds the attachment represented by the file name and stream in the specified parameter to the list item.

        :param AttachmentCreationInformation attachment_file_information: The creation information which contains file
            name and content stream.
        """
        if isinstance(attachment_file_information, dict):
            attachment_file_information = AttachmentCreationInformation(
                attachment_file_information.get('filename'),
                attachment_file_information.get('content')
            )

        return_type = Attachment(self.context)
        self.add_child(return_type)
        qry = ServiceOperationQuery(self,
                                    "add",
                                    {
                                        "filename": attachment_file_information.filename,
                                    },
                                    attachment_file_information.content,
                                    None,
                                    return_type)
        self.context.add_query(qry)
        return return_type

    def add_using_path(self, decoded_url, content_stream):
        """
        Adds the attachment represented by the file name and stream in the specified parameter to the list item.

        :param str decoded_url: Specifies the path for the attachment file.
        :param str content_stream: Stream containing the content of the attachment.
        """
        return_type = Attachment(self.context)
        payload = {
            "DecodedUrl": decoded_url,
            "contentStream": content_stream
        }
        qry = ServiceOperationQuery(self, "AddUsingPath", None, payload, None, return_type)
        self.context.add_query(qry)
        self.add_child(return_type)
        return return_type

    def get_by_filename(self, filename):
        """Retrieve Attachment file object by filename

        :param str filename: The specified file name.
        """
        return Attachment(self.context, ServiceOperationPath("GetByFileName", [filename], self.resource_path))

    def get_by_filename_as_path(self, decoded_url):
        """Get the attachment file.

        :param str decoded_url: The specified file name.
        """
        return Attachment(self.context, ServiceOperationPath("GetByFileNameAsPath", [decoded_url], self.resource_path))
