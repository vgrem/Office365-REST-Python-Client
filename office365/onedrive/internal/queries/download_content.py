from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery


def create_download_content_query(file_item, format_name=None):
    """
    :type file_item: office365.onedrive.driveItem.DriveItem
    :type format_name: str or None
    """
    return_type = ClientResult(file_item.context)
    action_name = "content"
    if format_name is not None:
        action_name = action_name + r"?format={0}".format(format_name)
    return FunctionQuery(file_item, action_name, None, return_type)


def create_download_session_content_query(file_item, format_name=None):
    """
    :type file_item: office365.onedrive.driveItem.DriveItem
    :type format_name: str or None
    """
    action_name = "content"
    if format_name is not None:
        action_name = action_name + r"?format={0}".format(format_name)
    return ServiceOperationQuery(file_item, action_name)
