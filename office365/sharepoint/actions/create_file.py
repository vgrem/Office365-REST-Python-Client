from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.files.file import File


class CreateFileQuery(ServiceOperationQuery):

    def __init__(self, files, file_creation_information):
        """

        :type file_creation_information: office365.sharepoint.files.file_creation_information.FileCreationInformation
        :type files: FileCollection
        """
        super().__init__(files, "add", file_creation_information.to_json(), file_creation_information.content, None,
                         File(files.context))
        files.add_child(self._return_type)
