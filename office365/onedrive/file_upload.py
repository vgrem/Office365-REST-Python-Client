import os

from office365.onedrive.driveItemUploadableProperties import DriveItemUploadableProperties
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

    def __init__(self, target_folder, source_path, chunk_size=1024, chunk_uploaded=None):
        """

        :type target_folder: office365.graph.onedrive.driveItem.DriveItem
        :type source_path: str
        :type chunk_size: int
        """
        self._chunk_size = chunk_size
        self._source_path = source_path
        self._file_name = os.path.basename(self._source_path)
        self._chunk_uploaded = chunk_uploaded
        # 1. create an empty file
        self._target_item = target_folder.upload(self._file_name, "")
        self._target_item.context.after_execute(self._execute_upload_session, True)

    def _execute_upload_session(self, resp):
        item = DriveItemUploadableProperties()
        item.name = self._file_name
        self._session_result = self._target_item.create_upload_session(item)
        self.context.execute_query()

        fh = open(self._source_path, 'rb')
        st = os.stat(self._source_path)
        f_pos = 0
        for piece in read_in_chunks(fh, chunk_size=self._chunk_size):
            req = RequestOptions(self._session_result.value.uploadUrl)
            req.method = HttpMethod.Put
            req.set_header('Content-Length', str(len(piece)))
            req.set_header('Content-Range', 'bytes {0}-{1}/{2}'.format(f_pos, (f_pos + len(piece) - 1), st.st_size))
            req.set_header('Accept', '*/*')
            req.data = piece
            self.context.execute_request_direct(req)
            f_pos += len(piece)
            if callable(self._chunk_uploaded):
                self._chunk_uploaded(f_pos)

    @property
    def context(self):
        return self._target_item.context

    @property
    def drive_item(self):
        return self._target_item
