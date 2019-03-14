import os

from settings import settings
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.file import File
from office365.sharepoint.file_creation_information import FileCreationInformation


def read_folder_and_files(context, list_title):
    """Read a folder example"""
    list_obj = context.web.lists.get_by_title(list_title)
    folder = list_obj.root_folder
    context.load(folder)
    context.execute_query()
    print("List url: {0}".format(folder.properties["ServerRelativeUrl"]))

    files = folder.files
    context.load(files)
    context.execute_query()
    for cur_file in files:
        print("File name: {0}".format(cur_file.properties["Name"]))

    folders = context.web.folders
    context.load(folders)
    context.execute_query()
    for folder in folders:
        print("Folder name: {0}".format(folder.properties["Name"]))


def upload_file_into_library(target_library, name, content):
    context = target_library.context
    info = FileCreationInformation()
    info.content = content
    info.url = name
    info.overwrite = True
    target_file = target_library.root_folder.files.add(info)
    context.execute_query()
    return target_file


def upload_file(context):
    upload_into_library = False
    path = "../tests/data/SharePoint User Guide.docx"
    with open(path, 'rb') as content_file:
        file_content = content_file.read()

    if upload_into_library:
        list_title = "Documents"
        library = context.web.lists.get_by_title(list_title)
        file = upload_file_into_library(library, os.path.basename(path), file_content)
        print("File url: {0}".format(file.properties["ServerRelativeUrl"]))
    else:
        target_url = "/Shared Documents/{0}".format(os.path.basename(path))
        File.save_binary(context, target_url, file_content)


def download_file(context):
    response = File.open_binary(context, "/Shared Documents/SharePoint User Guide.docx")
    with open("./data/SharePoint User Guide.docx", "wb") as local_file:
        local_file.write(response.content)


if __name__ == '__main__':
    ctx_auth = AuthenticationContext(url=settings['url'])
    if ctx_auth.acquire_token_for_user(username=settings['user_credentials']['username'],
                                       password=settings['user_credentials']['password']):
        ctx = ClientContext(settings['url'], ctx_auth)
        # read_folder_and_files(ctx)
        # upload_file(ctx)
        download_file(ctx)
    else:
        print(ctx_auth.get_last_error())
