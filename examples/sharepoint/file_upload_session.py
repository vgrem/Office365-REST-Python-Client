from settings import settings
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext


def print_upload_progress(offset):
    print ("Uploaded '{0}' bytes...".format(offset))


if __name__ == '__main__':
    site_url = settings['url']
    ctx_auth = AuthenticationContext(url=site_url)
    if ctx_auth.acquire_token_for_user(username=settings['user_credentials']['username'],
                                       password=settings['user_credentials']['password']):
        ctx = ClientContext(site_url, ctx_auth)

        # size_4k = 1024 * 4
        size_1Mb = 1000000
        local_path = "../../tests/data/big_buck_bunny.mp4"
        target_url = "/Shared Documents"
        # result_file = upload_file_session(ctx, target_url, local_path, size_1Mb)

        result_file = ctx.web.get_folder_by_server_relative_url(target_url)\
            .files.create_upload_session(local_path, size_1Mb, print_upload_progress)
        ctx.execute_query()
        print ('File {0} has been uploaded successfully'.format(result_file.properties['ServerRelativeUrl']))
