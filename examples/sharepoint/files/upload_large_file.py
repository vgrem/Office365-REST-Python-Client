from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext


def print_upload_progress(offset):
    print("Uploaded '{0}' bytes...".format(offset))


if __name__ == '__main__':
    ctx = ClientContext.connect_with_credentials(settings['url'],
                                                 UserCredential(settings['user_credentials']['username'],
                                                                settings['user_credentials']['password']))
    size_1Mb = 1000000
    local_path = "../../../tests/data/big_buck_bunny.mp4"
    target_url = "/Shared Documents"
    result_file = ctx.web.get_folder_by_server_relative_url(target_url) \
        .files.create_upload_session(local_path, size_1Mb, print_upload_progress)
    ctx.execute_query()
    print('File {0} has been uploaded successfully'.format(result_file.serverRelativeUrl))
