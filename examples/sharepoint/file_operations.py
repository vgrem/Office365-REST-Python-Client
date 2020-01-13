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
    folder = list_obj.rootFolder
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


def upload_file(context):

    path = "../tests/data/SharePoint User Guide.docx"
    with open(path, 'rb') as content_file:
        file_content = content_file.read()

    list_title = "Documents"
    target_folder = context.web.lists.get_by_title(list_title).rootFolder
    info = FileCreationInformation()
    info.content = file_content
    info.url = os.path.basename(path)
    info.overwrite = True
    target_file = target_folder.files.add(info)
    context.execute_query()
    print("File url: {0}".format(target_file.properties["ServerRelativeUrl"]))


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
        # get a source file located in library 'Shared Documents'
        source_file = ctx.web.get_file_by_server_relative_url("/teams/DemoSite/Shared Documents/Guide.docx")
        # move a file into sub folder called 'Archive'
        source_file.moveto("/teams/DemoSite/Shared Documents/Archive/Guide.docx", 1)
        # execute a query
        ctx.execute_query()
    else:
        print(ctx_auth.get_last_error())
