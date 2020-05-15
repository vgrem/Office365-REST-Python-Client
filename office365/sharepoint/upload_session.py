import os
import uuid

from office365.runtime.client_result import ClientResult
from office365.sharepoint.file import File
from office365.sharepoint.file_creation_information import FileCreationInformation


def read_in_chunks(file_object, size=1024):
    """Lazy function (generator) to read a file piece by piece."""
    while True:
        data = file_object.read(size)
        if not data:
            break
        yield data


class UploadSession(object):
    def __init__(self, source_path, chunk_size, chunk_uploaded):
        self._chunk_size = chunk_size
        self._upload_id = str(uuid.uuid4())
        self._source_path = source_path
        self._chunk_uploaded = chunk_uploaded
        self._target_file = None
        self._uploaded_bytes = 0

    def build_query(self, files):
        st = os.stat(self._source_path)
        file_name = os.path.basename(self._source_path)

        # 1. create an empty target file
        info = FileCreationInformation()
        info.url = file_name
        info.overwrite = True
        self._target_file = files.add(info)

        # 2. upload a file in chunks
        f_pos = 0
        fh = open(self._source_path, 'rb')
        for piece in read_in_chunks(fh, size=self._chunk_size):
            if f_pos == 0:
                upload_result = files.get_by_url(file_name).start_upload(self._upload_id, piece)
            elif f_pos + len(piece) < st.st_size:
                upload_result = files.get_by_url(file_name).continue_upload(self._upload_id, f_pos, piece)
            else:
                self._target_file = files.get_by_url(file_name).finish_upload(self._upload_id, f_pos, piece)
            f_pos += len(piece)

        if self._chunk_uploaded is not None:
            files.context.afterExecuteOnce += self._process_chunk_upload

    def _process_chunk_upload(self, result_object):
        if isinstance(result_object, ClientResult):
            if 'StartUpload' in result_object.value:
                self._uploaded_bytes = int(result_object.value['StartUpload'])
            elif 'ContinueUpload' in result_object.value:
                self._uploaded_bytes = int(result_object.value['ContinueUpload'])
        elif isinstance(result_object, File):
            self._uploaded_bytes = int(result_object.properties['Length'])
        self._chunk_uploaded(self._uploaded_bytes)

    @property
    def file(self):
        return self._target_file
