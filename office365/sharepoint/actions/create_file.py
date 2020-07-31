from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.files.file import File


class CreateFileQuery(ServiceOperationQuery):

    def __init__(self, files, file_creation_information):
        """

        :type file_creation_information: office365.sharepoint.file_creation_information.FileCreationInformation
        :type files: FileCollection
        """
        self._return_type = File(files.context)
        super().__init__(files, "add", {
            "overwrite": file_creation_information.overwrite,
            "url": file_creation_information.url
        }, file_creation_information.content, None, self._return_type)
        files.add_child(self._return_type)
