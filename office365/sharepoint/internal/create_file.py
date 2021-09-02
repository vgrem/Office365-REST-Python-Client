from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.files.file import File


def create_file_query(files, file_creation_information):
    """
    :type file_creation_information: office365.sharepoint.files.file_creation_information.FileCreationInformation
    :type files: office365.sharepoint.files.file_collection.FileCollection
    """
    return_file = File(files.context)
    qry = ServiceOperationQuery(files, "add", file_creation_information.to_json(),
                                file_creation_information.content, None,
                                return_file)
    files.add_child(return_file)
    return qry
