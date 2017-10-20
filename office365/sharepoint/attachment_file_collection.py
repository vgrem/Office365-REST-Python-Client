from office365.runtime.action_type import ActionType
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ClientQuery
from office365.sharepoint.attachment_file_creation_information import AttachmentFileCreationInformation
from office365.sharepoint.file import File


class AttachmentFileCollection(ClientObjectCollection):
    """Represents a collection of AttachmentFile resources."""

    def add(self, attachment_file_information):
        """Creates an attachment"""
        if isinstance(attachment_file_information, dict):
            attachment_file_information = AttachmentFileCreationInformation(
                attachment_file_information.get('filename'),
                attachment_file_information.get('content')
            )

        file_new = File(self.context)
        qry = ClientQuery.service_operation_query(self,
                                                  ActionType.PostMethod,
                                                  "add",
                                                  {
                                                      "filename": attachment_file_information.filename,
                                                  },
                                                  attachment_file_information.content)
        self.context.add_query(qry, file_new)
        self.add_child(file_new)
        return file_new
