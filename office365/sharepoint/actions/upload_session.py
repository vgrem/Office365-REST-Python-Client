import os
import uuid

from office365.runtime.client_result import ClientResult
from office365.sharepoint.actions.create_file import CreateFileQuery
from office365.sharepoint.files.file import File
from office365.sharepoint.files.file_creation_information import FileCreationInformation


def read_in_chunks(file_object, size=1024):
    """Lazy function (generator) to read a file piece by piece."""
    while True:
        data = file_object.read(size)
        if not data:
            break
        yield data


def _create_empty_file(path):
    file_name = os.path.basename(path)
    info = FileCreationInformation()
    info.url = file_name
    info.overwrite = True
    return info


class UploadSessionQuery(CreateFileQuery):
    def __init__(self, files, source_path, chunk_size, chunk_uploaded):
        """

        :type files: office365.sharepoint.files.file_collection.FileCollection
        :type source_path: str
        :type chunk_size: int
        :type chunk_uploaded: (int)->None
        """

        super().__init__(files, _create_empty_file(source_path))
        self._chunk_size = chunk_size
        self._upload_id = str(uuid.uuid4())
        self._source_path = source_path
        self._chunk_uploaded = chunk_uploaded
        self._uploaded_bytes = 0
        self._upload_results = []
        self.file.context.after_execute(self._build_upload_session_query)

    def _build_upload_session_query(self, response):
        st = os.stat(self._source_path)
        # upload a file in chunks
        f_pos = 0
        fh = open(self._source_path, 'rb')
        for piece in read_in_chunks(fh, size=self._chunk_size):
            if f_pos == 0:
                upload_result = self.file.start_upload(self._upload_id, piece)
                self._upload_results.append(upload_result)
            elif f_pos + len(piece) < st.st_size:
                upload_result = self.file.continue_upload(self._upload_id, f_pos, piece)
                self._upload_results.append(upload_result)
            else:
                self._return_type = self.file.finish_upload(self._upload_id, f_pos, piece)
            f_pos += len(piece)
        fh.close()

        if callable(self._chunk_uploaded):
            self.file.context.after_execute(self._process_chunk_upload)

    def _process_chunk_upload(self, resp):
        qry = self.file.context.current_query
        if isinstance(qry.return_type, ClientResult):
            self._uploaded_bytes = int(qry.return_type.value)
            self.file.context.after_execute(self._process_chunk_upload)
        elif isinstance(self._return_type, File):
            self._uploaded_bytes = qry.return_type.length
        self._chunk_uploaded(self._uploaded_bytes)

    @property
    def file(self):
        """
        :rtype: File
        """
        return self.return_type
