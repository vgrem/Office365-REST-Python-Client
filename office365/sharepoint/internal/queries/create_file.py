from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.files.creation_information import FileCreationInformation
from office365.sharepoint.files.file import File


def create_file_query(binding_type, name, content=None):
    """
    Constructs a query to create/upload a file

    :type name: str
    :type content: str or None
    :type binding_type: office365.sharepoint.files.collection.FileCollection
    """
    return_type = File(binding_type.context)
    binding_type.add_child(return_type)
    create_info = FileCreationInformation(url=name, overwrite=True)
    qry = ServiceOperationQuery(binding_type, "add", create_info.to_json(), content, None, return_type)
    return qry
