import os
import uuid

from office365.sharepoint.file_creation_information import FileCreationInformation
from settings import settings
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext


def read_in_chunks(file_object, size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(size)
        if not data:
            break
        yield data


if __name__ == '__main__':
    site_url = settings['url']
    ctx_auth = AuthenticationContext(url=site_url)
    if ctx_auth.acquire_token_for_user(username=settings['user_credentials']['username'],
                                       password=settings['user_credentials']['password']):
        ctx = ClientContext(site_url, ctx_auth)

        upload_id = str(uuid.uuid4())
        size_4k = 1024 * 4
        local_path = "../data/SharePoint User Guide.docx"
        f = open(local_path, 'rb')
        st = os.stat(local_path)
        f_pos = 0
        target_folder_url = "/Shared Documents"

        # 1. create an empty file first
        info = FileCreationInformation()
        info.content = ""
        info.url = os.path.basename(local_path)
        info.overwrite = True
        target_folder = ctx.web.get_folder_by_server_relative_url(target_folder_url)
        target_file = target_folder.files.add(info)
        ctx.execute_query()

        # 2. upload a file via session
        target_file_url = os.path.basename(local_path)
        for piece in read_in_chunks(f, size=size_4k):
            if f_pos == 0:
                upload_result = target_folder.files.get_by_url(target_file_url).start_upload(upload_id, piece)
                ctx.execute_query()
            elif f_pos + len(piece) < st.st_size:
                upload_result = target_folder.files.get_by_url(target_file_url).continue_upload(upload_id, f_pos,
                                                                                                piece)
                ctx.execute_query()
            else:
                upload_result = target_folder.files.get_by_url(target_file_url).finish_upload(upload_id, f_pos, piece)
                ctx.execute_query()
            f_pos += len(piece)

        ctx.execute_query()
    else:
        print(ctx_auth.get_last_error())
