import os

from office365.graph.onedrive.driveItemUploadableProperties import DriveItemUploadableProperties
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions


def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


class ResumableFileUpload(object):
    """Create an upload session to allow your app to upload files up to the maximum file size. An upload session
    allows your app to upload ranges of the file in sequential API requests, which allows the transfer to be resumed
    if a connection is dropped while the upload is in progress. """
    def __init__(self, target_folder, source_path, chunk_size):
        self._target_folder = target_folder
        self._chunk_size = chunk_size
        self._source_path = source_path
        self._uploaded_bytes = 0

    def execute(self, chunk_uploaded=None):
        ctx = self._target_folder.context
        file_name = os.path.basename(self._source_path)
        # 1. create an empty file
        target_item = self._target_folder.upload(file_name, None)
        ctx.execute_query()

        # 2. create upload session
        item = DriveItemUploadableProperties()
        item.name = file_name
        session_result = target_item.create_upload_session(item)
        ctx.execute_query()

        # 3. start upload
        fh = open(self._source_path, 'rb')
        st = os.stat(self._source_path)
        f_pos = 0
        for piece in read_in_chunks(fh, chunk_size=self._chunk_size):
            req = RequestOptions(session_result.value.uploadUrl)
            req.method = HttpMethod.Put
            req.set_header('Content-Length', str(len(piece)))
            req.set_header('Content-Range', 'bytes {0}-{1}/{2}'.format(f_pos, (f_pos + len(piece) - 1), st.st_size))
            req.set_header('Accept', '*/*')
            req.data = piece
            resp = ctx.execute_request_direct(req)
            f_pos += len(piece)
            if chunk_uploaded is not None:
                chunk_uploaded(f_pos)

        return target_item
