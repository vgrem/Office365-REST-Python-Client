import os

from office365.onedrive.driveItem import DriveItem
from office365.onedrive.driveItemUploadableProperties import DriveItemUploadableProperties
from office365.resource_path_url import ResourcePathUrl
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.client_query import ClientQuery


class ResumableFileUpload(ClientQuery):
    """Create an upload session to allow your app to upload files up to the maximum file size. An upload session
    allows your app to upload ranges of the file in sequential API requests, which allows the transfer to be resumed
    if a connection is dropped while the upload is in progress. """

    def __init__(self, target_folder, source_path, chunk_size=1024, chunk_uploaded=None):
        """

        :type target_folder: office365.onedrive.driveItem.DriveItem
        :type source_path: str
        :type chunk_size: int
        """
        super(ResumableFileUpload, self).__init__(target_folder.context, target_folder)
        self._file_handle = None
        self._chunk_size = chunk_size
        self._range_start = 0
        self._range_end = 0
        self._range_data = None
        self._chunk_uploaded = chunk_uploaded
        self._source_path = source_path
        self._session_result = self._create_upload_session()
        self._range_queries = []
        self._read_completed = False

    def _create_upload_session(self):
        item = DriveItemUploadableProperties()
        item.name = self.file_name
        result = self.return_type.create_upload_session(item)
        self.context.after_execute(self._create_next_range_query)
        return result

    def _create_next_range_query(self, resp):
        if self._read_next_chunk():
            qry = ClientQuery(self.context, self.return_type)
            self.context.before_execute(self._construct_range_request)
            self.context.after_execute(self._create_next_range_query)
            self.context.after_execute(self._notify_after_uploaded)
            self.context.add_query(qry, True)

    def _construct_range_request(self, request):
        request.url = self._session_result.value.uploadUrl
        request.method = HttpMethod.Put
        request.set_header('Content-Length', str(len(self._range_data)))
        request.set_header('Content-Range', 'bytes {0}-{1}/{2}'.format(self._range_start, self._range_end - 1, self.file_size))
        request.set_header('Accept', '*/*')
        request.data = self._range_data

    def _notify_after_uploaded(self, response):
        response.raise_for_status()
        if callable(self._chunk_uploaded):
            self._chunk_uploaded(self._range_end)

    def _read_next_chunk(self):
        if self._read_completed:
            return False
        if self._file_handle is None:
            self._file_handle = open(self._source_path, 'rb')
        self._range_start = self._file_handle.tell()
        self._range_data = self._file_handle.read(self._chunk_size)
        if not self._range_data:
            return False
        self._range_end = self._file_handle.tell()
        if self._range_end >= self.file_size:
            self._file_handle.close()
            self._read_completed = True
        return True

    @property
    def file_size(self):
        return os.stat(self._source_path).st_size

    @property
    def file_name(self):
        return os.path.basename(self._source_path)

    @property
    def return_type(self):
        return DriveItem(self.context, ResourcePathUrl(self.file_name, self.binding_type.resource_path))
