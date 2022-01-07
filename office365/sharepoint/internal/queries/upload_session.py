import os
import uuid

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.internal.queries.create_file import create_file_query
from office365.sharepoint.files.file import File
from office365.sharepoint.files.file_creation_information import FileCreationInformation


class UploadSessionQuery(ServiceOperationQuery):
    def __init__(self, files, source_path, chunk_size, chunk_uploaded, chunk_func_args):
        """

        :type files: office365.sharepoint.files.file_collection.FileCollection
        :type source_path: str
        :type chunk_size: int
        :type chunk_uploaded: (int, *)->None
        """

        super(UploadSessionQuery, self).__init__(files)
        self._chunk_size = chunk_size
        self._upload_id = str(uuid.uuid4())
        self._source_path = source_path
        self._chunk_uploaded = chunk_uploaded
        self._chunk_func_args = chunk_func_args
        self._bytes_read = 0
        self._upload_result = None
        self._file_handle = None
        self._file_query = self._build_empty_file_query(files)

    def _build_empty_file_query(self, files):
        info = FileCreationInformation()
        info.url = self.file_name
        info.overwrite = True

        qry = create_file_query(files, info)
        self.context.after_execute(self._build_upload_session_query)
        return qry

    def _read_next_chunk(self):
        data = self._file_handle.read(self._chunk_size)
        self._bytes_read = self._file_handle.tell()
        return data

    def _has_pending_read(self):
        if self._bytes_read >= self.file_size:
            if self._file_handle is not None:
                self._file_handle.close()
            return False
        if self._file_handle is None:
            self._file_handle = open(self._source_path, 'rb')
        return True

    def _build_upload_session_query(self, response):
        """
        :type response: requests.Response
        """
        response.raise_for_status()

        qry = self.context.current_query
        uploaded_bytes = 0
        if isinstance(qry.return_type, ClientResult):
            uploaded_bytes = int(qry.return_type.value)
        elif isinstance(qry.return_type, File):
            uploaded_bytes = qry.return_type.length

        if callable(self._chunk_uploaded):
            self._chunk_uploaded(uploaded_bytes, *self._chunk_func_args)

        if self._has_pending_read():
            piece = self._read_next_chunk()
            if uploaded_bytes == 0:
                self._upload_result = self.return_type.start_upload(self._upload_id, piece)
            elif uploaded_bytes + len(piece) < self.file_size:
                self._upload_result = self.return_type.continue_upload(self._upload_id, uploaded_bytes, piece)
            else:
                self._return_type = self.return_type.finish_upload(self._upload_id, uploaded_bytes, piece)
            self.context.after_execute(self._build_upload_session_query)

    @property
    def url(self):
        return self._file_query.url

    @property
    def return_type(self):
        """
        :rtype: File
        """
        return self._file_query.return_type

    @property
    def binding_type(self):
        return self._file_query.binding_type

    @property
    def file_name(self):
        return os.path.basename(self._source_path)

    @property
    def file_size(self):
        st = os.stat(self._source_path)
        return st.st_size
