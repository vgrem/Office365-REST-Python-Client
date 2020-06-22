from office365.runtime.queries.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.files.file import File


class CreateFileQuery(ServiceOperationQuery):

    def __init__(self, container, file_creation_information):
        """

        :type file_creation_information: office365.sharepoint.file_creation_information.FileCreationInformation
        :type container: FileCollection
        """
        self._return_type = File(container.context)
        super().__init__(container, "add", {
            "overwrite": file_creation_information.overwrite,
            "url": file_creation_information.url
        }, file_creation_information.content, None, self._return_type)
        container.add_child(self._return_type)
