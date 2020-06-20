import os
import uuid

from office365.runtime.client_result import ClientResult
from office365.sharepoint.files.file import File
from office365.sharepoint.files.file_creation_information import FileCreationInformation
from office365.sharepoint.actions.create_file import CreateFileQuery


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
    def __init__(self, container, source_path, chunk_size, chunk_uploaded):
        """

        :type container: office365.sharepoint.file_collection.FileCollection
        :type source_path: str
        :type chunk_size: int
        :type chunk_uploaded: (int)->None
        """

        super().__init__(container, _create_empty_file(source_path))
        self._chunk_size = chunk_size
        self._upload_id = str(uuid.uuid4())
        self._source_path = source_path
        self._chunk_uploaded = chunk_uploaded
        self._uploaded_bytes = 0
        self._upload_results = []
        container.context.afterExecuteOnce += self._build_upload_query

    def _build_upload_query(self, target_file):
        """

        :type target_file: File
        """
        st = os.stat(self._source_path)

        # upload a file in chunks
        f_pos = 0
        fh = open(self._source_path, 'rb')
        for piece in read_in_chunks(fh, size=self._chunk_size):
            if f_pos == 0:
                upload_result = target_file.start_upload(self._upload_id, piece)
                self._upload_results.append(upload_result)
            elif f_pos + len(piece) < st.st_size:
                upload_result = target_file.continue_upload(self._upload_id, f_pos, piece)
                self._upload_results.append(upload_result)
            else:
                self._return_type = target_file.finish_upload(self._upload_id, f_pos, piece)
            f_pos += len(piece)
        fh.close()
        if self._chunk_uploaded is not None:
            self._binding_type.context.afterExecuteOnce += self._process_chunk_upload

    def _process_chunk_upload(self, result_object):
        self._binding_type.context.afterExecuteOnce += self._process_chunk_upload
        if isinstance(result_object, ClientResult):
            self._uploaded_bytes = int(result_object.value)
        elif isinstance(result_object, File):
            self._uploaded_bytes = int(result_object.properties['Length'])
        self._chunk_uploaded(self._uploaded_bytes)

    @property
    def file(self):
        return self.return_type
