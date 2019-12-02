import json
import os

from settings import settings

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.caml_query import CamlQuery
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.file import File
from office365.sharepoint.file_creation_information import FileCreationInformation


def read_folder_and_files_alt(context, list_title):
    """Read a folder example"""
    list_obj = context.web.lists.get_by_title(list_title)
    qry = CamlQuery.create_all_items_query()
    items = list_obj.get_items(qry)
    context.execute_query()
    for cur_item in items:
        print("File name: {0}".format(cur_item.properties["Title"]))


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


def upload_file_alt(target_folder, name, content):
    context = target_folder.context
    info = FileCreationInformation()
    info.content = content
    info.url = name
    info.overwrite = True
    target_file = target_folder.files.add(info)
    context.execute_query()
    return target_file


def upload_file(context):
    upload_into_library = True
    path = "../tests/data/SharePoint User Guide.docx"
    with open(path, 'rb') as content_file:
        file_content = content_file.read()

    if upload_into_library:
        list_title = "Documents"
        target_folder = context.web.lists.get_by_title(list_title).root_folder
        file = upload_file_alt(target_folder, os.path.basename(path), file_content)
        print("File url: {0}".format(file.properties["ServerRelativeUrl"]))
    else:
        target_url = "/Shared Documents/{0}".format(os.path.basename(path))
        File.save_binary(context, target_url, file_content)


def download_file(context):
    response = File.open_binary(context, "/Shared Documents/SharePoint User Guide.docx")
    with open("./data/SharePoint User Guide.docx", "wb") as local_file:
        local_file.write(response.content)


if __name__ == '__main__':
    site_url = 'https://mediadev8.sharepoint.com/teams/DemoSite/'

    ctx_auth = AuthenticationContext(url=site_url)
    if ctx_auth.acquire_token_for_user(username=settings['user_credentials']['username'],
                                       password=settings['user_credentials']['password']):
        # if ctx_auth.acquire_token_for_app(client_id=settings['client_credentials']['client_id'],
        #                                  client_secret=settings['client_credentials']['client_secret']):
        ctx = ClientContext(site_url, ctx_auth)
        # read_folder_and_files(ctx, "Documents")
        # read_folder_and_files_alt(ctx, "Documents")
        # upload_file(ctx)
        # download_file(ctx)
        # response = File.open_binary(ctx, "/teams/DemoSite/Shared Documents/Guide.docx")
        # with open("../data/SharePoint User Guide.docx", "wb") as local_file:
        #    local_file.write(response.content)

        # path = "../data/SharePoint User Guide.docx"
        # info = FileCreationInformation()
        # with open(path, 'rb') as content_file:
        #    info.content = content_file.read()
        # info.url = os.path.basename(path)
        # info.overwrite = True
        # target_list = ctx.web.lists.get_by_title("Documents")
        # target_file = target_list.root_folder.files.add(info)
        # ctx.execute_query()

        target_folder = ctx.web.folders.add("Shared Documents/Archive")
        ctx.execute_query()
    else:
        print(ctx_auth.get_last_error())
