import os
import uuid
from functools import partial

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.actions.create_file import create_file_query
from office365.sharepoint.files.file import File
from office365.sharepoint.files.file_creation_information import FileCreationInformation


def read_in_chunks(file_object, size=1024):
    """Lazy function (generator) to read a file piece by piece.

    :type size: int
    :type file_object: typing.IO
    """
    while True:
        data = file_object.read(size)
        if not data:
            break
        yield data


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
        self._uploaded_bytes = 0
        self._upload_results = []
        self._query = self._build_empty_file_query(files, source_path)

    def build_url(self):
        return self._query.build_url()

    def build_request(self):
        return self._query.build_request()

    def _build_empty_file_query(self, files, path):
        """
        :type files: office365.sharepoint.files.file_collection.FileCollection
        :type path: str
        """
        file_name = os.path.basename(path)
        info = FileCreationInformation()
        info.url = file_name
        info.overwrite = True

        qry = create_file_query(files, info)
        self.context.after_execute(self._build_upload_session_query)
        return qry

    def _build_upload_session_query(self, response):
        """
        :type response: requests.Response
        """
        st = os.stat(self._source_path)
        if callable(self._chunk_uploaded):
            self.context.after_execute(self._process_chunk_upload)
        # upload a file in chunks
        f_pos = 0
        with open(self._source_path, 'rb') as fh:
            for piece in iter(partial(fh.read, self._chunk_size), b''):
                if f_pos == 0:
                    upload_result = self.file.start_upload(self._upload_id, piece)
                    self._upload_results.append(upload_result)
                elif f_pos + len(piece) < st.st_size:
                    upload_result = self.file.continue_upload(self._upload_id, f_pos, piece)
                    self._upload_results.append(upload_result)
                else:
                    self._return_type = self.file.finish_upload(self._upload_id, f_pos, piece)
                f_pos += len(piece)

                self.context.execute_query()

    def _process_chunk_upload(self, resp):
        """
        :type resp: requests.Response
        """
        qry = self.context.current_query
        if isinstance(qry.return_type, ClientResult):
            self._uploaded_bytes = int(qry.return_type.value)
            self.file.context.after_execute(self._process_chunk_upload)
        elif isinstance(self._return_type, File):
            self._uploaded_bytes = qry.return_type.length
        self._chunk_uploaded(self._uploaded_bytes, *self._chunk_func_args)

    @property
    def return_type(self):
        """
        :rtype: File
        """
        return self._query.return_type

    @property
    def binding_type(self):
        return self._query.binding_type

    @property
    def file(self):
        """
        :rtype: File
        """
        return self.return_type
