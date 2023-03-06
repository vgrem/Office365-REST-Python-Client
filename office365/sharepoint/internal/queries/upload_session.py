import os
import uuid

from office365.runtime.client_result import ClientResult
from office365.sharepoint.internal.queries.create_file import create_file_query
from office365.sharepoint.files.file import File


def create_upload_session_query_ex(binding_type, path_or_file, chunk_size, chunk_uploaded, **kwargs):
    """
    :type binding_type: office365.sharepoint.files.collection.FileCollection
    :type path_or_file: typing.IO or str
    :type chunk_size: int
    :type chunk_uploaded: (int, *)->None
    """
    if hasattr(path_or_file, 'read'):
        return create_upload_session_query(binding_type, path_or_file, chunk_size, chunk_uploaded, **kwargs)
    else:
        f = open(path_or_file, 'rb')
        return create_upload_session_query(binding_type, f, chunk_size, chunk_uploaded, True, **kwargs)


def create_upload_session_query(binding_type, file_object, chunk_size, chunk_uploaded, force_close=False,
                                file_size=None, file_name=None, **kwargs):
    """
    :type binding_type: office365.sharepoint.files.collection.FileCollection
    :type file_object: typing.IO
    :type chunk_size: int
    :type force_close: bool
    :type chunk_uploaded: (int, *)->None
    :type file_size: int
    :type file_name: str
    """

    upload_id = str(uuid.uuid4())
    file_size = file_size if file_size else os.fstat(file_object.fileno()).st_size
    file_name = file_name if file_name else os.path.basename(file_object.name)

    def _read_next():
        return file_object.read(chunk_size)

    def _has_pending_read():
        bytes_read = file_object.tell()
        return bytes_read < file_size

    def _run_upload(response, return_type, next_return_type=None):
        """
        :type return_type: File
        :type response: requests.Response
        """
        response.raise_for_status()

        uploaded_bytes = 0
        if isinstance(next_return_type, ClientResult):
            uploaded_bytes = int(next_return_type.value)
        elif isinstance(next_return_type, File):
            uploaded_bytes = next_return_type.length

        if callable(chunk_uploaded):
            chunk_uploaded(uploaded_bytes, **kwargs)

        if not _has_pending_read():
            if force_close and not file_object.closed:
                file_object.close()
            return

        content = _read_next()
        if uploaded_bytes == 0:
            next_return_type = return_type.start_upload(upload_id, content)
        elif uploaded_bytes + len(content) < file_size:
            next_return_type = return_type.continue_upload(upload_id, uploaded_bytes, content)
        else:
            next_return_type = return_type.finish_upload(upload_id, uploaded_bytes, content)
        binding_type.context.after_execute(_run_upload, return_type=return_type, next_return_type=next_return_type)

    if file_size > chunk_size:
        qry = create_file_query(binding_type, file_name)
        binding_type.context.after_execute(_run_upload, return_type=qry.return_type, next_return_type=qry.return_type)
        return qry
    else:
        return create_file_query(binding_type, file_name, file_object.read())
