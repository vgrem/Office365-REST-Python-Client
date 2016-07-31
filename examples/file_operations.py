from client.office365.runtime.auth.authentication_context import AuthenticationContext
from client.office365.sharepoint.client_context import ClientContext
from settings import settings


def read_folder_and_files():
    """Read a folder example"""
    list_obj = ctx.web.lists.get_by_title(listTitle)
    folder = list_obj.root_folder
    ctx.load(folder)
    ctx.execute_query()
    print "List url: {0}".format(folder.properties["ServerRelativeUrl"])

    files = folder.files
    ctx.load(files)
    ctx.execute_query()
    for cur_file in files:
        print "File name: {0}".format(cur_file.properties["Name"])

    folders = ctx.web.folders
    ctx.load(folders)
    ctx.execute_query()
    for folder in folders:
        print "Folder name: {0}".format(folder.properties["Name"])


if __name__ == '__main__':
    ctx_auth = AuthenticationContext(url=settings['url'])
    if ctx_auth.acquire_token_for_user(username=settings['username'], password=settings['password']):
        ctx = ClientContext(settings['url'], ctx_auth)

        listTitle = "Documents"
        read_folder_and_files()

    else:
        print ctx_auth.get_last_error()
