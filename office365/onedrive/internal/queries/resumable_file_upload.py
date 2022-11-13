import os

from office365.onedrive.driveitems.uploadable_properties import DriveItemUploadableProperties
from office365.runtime.odata.v4.upload_session_request import UploadSessionRequest
from office365.runtime.queries.upload_session import UploadSessionQuery


def create_resumable_file_upload_query(return_type, local_path, chunk_size, chunk_uploaded):
    """
    :type return_type: office365.onedrive.driveitems.driveItem.DriveItem
    :type local_path: str
    :type chunk_size: int
    :type chunk_uploaded: (int)->None
    """
    item = DriveItemUploadableProperties()
    item.name = os.path.basename(local_path)
    qry = UploadSessionQuery(return_type, {"item": item})
    context = return_type.context

    def _start_upload(resp):
        """
        :type resp: requests.Response
        """
        resp.raise_for_status()
        with open(local_path, 'rb') as local_file:
            session_request = UploadSessionRequest(local_file, chunk_size, chunk_uploaded)
            session_request.execute_query(qry)
    context.after_execute(_start_upload)
    return qry
