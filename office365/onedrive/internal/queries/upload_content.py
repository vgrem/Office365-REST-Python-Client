from office365.onedrive.internal.paths.url import UrlPath
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation import ServiceOperationQuery


def create_upload_content_query(folder_item, name, content=None):
    """

    :param office365.onedrive.driveItem.DriveItem folder_item: Folder (container)
    :param str name: a file name
    :param str content: a file content
    """
    from office365.onedrive.driveitems.driveItem import DriveItem
    file_item = DriveItem(folder_item.context, UrlPath(name, folder_item.resource_path))
    qry = ServiceOperationQuery(file_item, "content", None, content, None, file_item)

    def _modify_query(request):
        """
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        request.method = HttpMethod.Put
    folder_item.context.before_execute(_modify_query)
    return qry
