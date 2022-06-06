from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.files.file import File


def create_file_query(files, file_create_info):
    """
    :type file_create_info: office365.sharepoint.files.creation_information.FileCreationInformation
    :type files: office365.sharepoint.files.collection.FileCollection
    """
    return_file = File(files.context)
    qry = ServiceOperationQuery(files, "add", file_create_info.to_json(), file_create_info.content, None, return_file)
    files.add_child(return_file)
    return qry
