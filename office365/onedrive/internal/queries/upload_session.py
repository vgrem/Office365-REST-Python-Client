import os
from abc import abstractmethod

from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.client_query import ClientQuery


class UploadSessionQuery(ClientQuery):
    """Create an upload session to allow your app to upload files up to the maximum file size. An upload session
    allows your app to upload ranges of the file in sequential API requests, which allows the transfer to be resumed
    if a connection is dropped while the upload is in progress. """

    def __init__(self, session_item, source_path, chunk_size=1024, chunk_uploaded=None):
        """

        :type session_item: office365.entity.Entity
        :type source_path: str
        :type chunk_size: int
        """
        super(UploadSessionQuery, self).__init__(session_item.context, session_item)
        self._file_handle = None
        self._chunk_size = chunk_size
        self._range_start = 0
        self._range_end = 0
        self._chunk_uploaded = chunk_uploaded
        self._source_path = source_path
        self._session_result = None
        self._session_result = self.create_upload_session()
        self.context.after_execute(self._create_next_range_query)

    @abstractmethod
    def create_upload_session(self):
        pass

    def _create_next_range_query(self, resp):
        """
        :type resp: requests.Response
        """
        if self._has_pending_read():
            qry = ClientQuery(self.context, self.binding_type)
            self.context.before_execute(self._construct_range_request)
            self.context.after_execute(self._create_next_range_query)
            self.context.after_execute(self._notify_after_uploaded)
            self.context.add_query(qry, True)

    def _construct_range_request(self, request):
        """
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        range_data = self._read_next_chunk()
        request.url = self._session_result.value.uploadUrl
        request.method = HttpMethod.Put
        request.set_header('Content-Length', str(len(range_data)))
        request.set_header('Content-Range',
                           'bytes {0}-{1}/{2}'.format(self._range_start, self._range_end - 1, self.file_size))
        request.set_header('Accept', '*/*')
        request.data = range_data

    def _notify_after_uploaded(self, response):
        """
        :type response: requests.Response
        """
        response.raise_for_status()
        if callable(self._chunk_uploaded):
            self._chunk_uploaded(self._range_end)

    def _read_next_chunk(self):
        self._range_start = self._file_handle.tell()
        range_data = self._file_handle.read(self._chunk_size)
        self._range_end = self._file_handle.tell()
        return range_data

    def _has_pending_read(self):
        if self._range_end >= self.file_size:
            if self._file_handle is not None:
                self._file_handle.close()
            return False
        if self._file_handle is None:
            self._file_handle = open(self._source_path, 'rb')
        return True

    @property
    def file_size(self):
        return os.stat(self._source_path).st_size

    @property
    def file_name(self):
        return os.path.basename(self._source_path)
