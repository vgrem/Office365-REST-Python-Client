import os
import uuid

from office365.runtime.client_result import ClientResult
from office365.sharepoint.internal.queries.create_file import create_file_query
from office365.sharepoint.files.file import File
from office365.sharepoint.files.creation_information import FileCreationInformation


def create_upload_session_query(binding_type, source_path, chunk_size, chunk_uploaded, **kwargs):
    """
    :type binding_type: office365.sharepoint.files.collection.FileCollection
    :type source_path: str
    :type chunk_size: int
    :type chunk_uploaded: (int, *)->None
    """
    create_info = FileCreationInformation()
    create_info.url = os.path.basename(source_path)
    create_info.overwrite = True

    context = binding_type.context
    qry = create_file_query(binding_type, create_info)
    upload_id = str(uuid.uuid4())
    file_size = os.stat(source_path).st_size

    def _read_next(file_object):
        return file_object.read(chunk_size)

    def _has_pending_read(file_object):
        bytes_read = file_object.tell()
        if bytes_read >= file_size:
            file_object.close()
            return False
        return True

    def _start_upload(resp):
        file_object = open(source_path, 'rb')
        _upload_next(resp, file_object=file_object, return_type=qry.return_type)

    def _upload_next(response, file_object, return_type):
        """
        :type response: requests.Response
        """
        response.raise_for_status()

        uploaded_bytes = 0
        if isinstance(return_type, ClientResult):
            uploaded_bytes = int(return_type.value)
        elif isinstance(return_type, File):
            uploaded_bytes = return_type.length

        if callable(chunk_uploaded):
            chunk_uploaded(uploaded_bytes, **kwargs)

        if not _has_pending_read(file_object):
            return

        content = _read_next(file_object)
        if uploaded_bytes == 0:
            next_return_type = qry.return_type.start_upload(upload_id, content)
        elif uploaded_bytes + len(content) < file_size:
            next_return_type = qry.return_type.continue_upload(upload_id, uploaded_bytes, content)
        else:
            next_return_type = qry.return_type.finish_upload(upload_id, uploaded_bytes, content)
        context.after_execute(_upload_next, file_object=file_object, return_type=next_return_type)

    context.after_execute(_start_upload)
    return qry
