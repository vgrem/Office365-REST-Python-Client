import os

from office365.onedrive.driveitems.drive_item_uploadable_properties import DriveItemUploadableProperties
from office365.runtime.odata.v4.upload_session_request import UploadSessionRequest
from office365.runtime.queries.upload_session import UploadSessionQuery


def create_resumable_file_upload_query(return_type, source_path, chunk_size, chunk_uploaded):
    """
    :type return_type: office365.onedrive.driveitems.driveItem.DriveItem
    :type source_path: str
    :type chunk_size: int
    :type chunk_uploaded: (int)->None
    """
    item = DriveItemUploadableProperties()
    item.name = os.path.basename(source_path)
    qry = UploadSessionQuery(return_type, {"item": item})
    context = return_type.context

    def _upload_session(resp):
        """
        :type resp: requests.Response
        """
        resp.raise_for_status()
        with open(source_path, 'rb') as source_file:
            session_request = UploadSessionRequest(context, source_file, chunk_size)
            session_request.add_query(qry)

            def _process_response(response):
                """
                :type response: requests.Response
                """
                response.raise_for_status()
                if callable(chunk_uploaded):
                    chunk_uploaded(session_request.range_end)
            session_request.afterExecute += _process_response
            session_request.execute_query()
    context.after_execute(_upload_session)
    return qry

