import logging
import os

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.caml_query import CamlQuery
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.file import File
from office365.sharepoint.file_creation_information import FileCreationInformation
from office365.sharepoint.querystring_builder import QueryStringBuilder

logger = logging.getLogger(__name__)


class SharePointClientException(Exception):
    """SharePoint Exception when initializing the client"""


class SharePointClient:
    """Client to access SharePoint Document Library"""

    def __init__(self, url, relative_url, folder, username, password) -> None:
        self.site_path = url
        self.relative_url = relative_url
        self.folder = folder

        ctx_auth = AuthenticationContext(url=self.site_path)
        if ctx_auth.acquire_token_for_user(username=username, password=password):
            self.context = ClientContext(self.site_path, ctx_auth)
        else:
            logger.exception(ctx_auth.get_last_error())
            raise SharePointClientException(ctx_auth.get_last_error())

    def get_folder(self, list_title):
        list_obj = self.context.web.lists.get_by_title(list_title)
        folder = list_obj.root_folder
        self.context.load(folder)
        self.context.execute_query()
        logger.info('List url: {}'.format(folder.properties["ServerRelativeUrl"]))
        return folder

    def read_folders(self, list_title):
        self.get_folder(list_title)
        folders = self.context.web.folders
        self.context.load(folders)
        self.context.execute_query()
        for folder in folders:
            logger.info('Folder name: {}'.format(folder.properties["Name"]))
        return folders

    def read_files(self, filters=dict):
        querystring = QueryStringBuilder(filters).get_querystring()
        folder = self.get_folder(self.folder)
        files = folder.files.filter(querystring)
        self.context.load(files)
        self.context.execute_query()
        for cur_file in files:
            logger.info('File name: {}'.format({cur_file.properties["Name"]}))
        return files

    def read_items(self, filters=dict):
        querystring = QueryStringBuilder(filters).get_querystring()
        list_object = self.context.web.lists.get_by_title(self.folder)
        items = list_object.get_items().filter(querystring)
        self.context.load(items)
        self.context.execute_query()
        return items

    def read_file(self, filename, extension):
        folder = self.get_folder(self.folder)
        cur_file = folder.files.get_by_url('/{}/{}/{}.{}'.format(self.relative_url, self.folder, filename, extension))
        self.context.load(cur_file)
        self.context.execute_query()
        logger.info('File name: {}'.format(cur_file.properties["Name"]))
        return cur_file

    def read_folder_and_files_alt(self, list_title):
        list_obj = self.context.web.lists.get_by_title(list_title)
        # TODO here create create custom CamlQuery if filter are passed
        qry = CamlQuery.create_all_items_query()
        items = list_obj.get_items(qry)
        self.context.load(items)
        self.context.execute_query()
        for cur_item in items:
            logger.info('File name: {}'.format(cur_item.properties["Title"]))
        return items

    def upload_file_alt(self, target_folder, name, content):
        context = target_folder.context
        info = FileCreationInformation()
        info.content = content
        info.url = name
        info.overwrite = True
        target_file = target_folder.files.add(info)
        context.execute_query()
        return target_file

    def upload_file(self, path, list_title, upload_into_library=True):
        with open(path, 'rb') as content_file:
            file_content = content_file.read()

        if upload_into_library:
            target_folder = self.context.web.lists.get_by_title(list_title).root_folder
            file = self.upload_file_alt(target_folder, os.path.basename(path), file_content)
            logger.info('File url: {}'.format(file.properties['ServerRelativeUrl']))
        else:
            target_url = '/{}/{}'.format(self.folder, os.path.basename(path))
            File.save_binary(self.context, target_url, file_content)

    def download_file(self, filename):
        response = File.open_binary(self.context, '/{}/{}'.format(self.folder, filename))
        with open('./data/{}'.format(filename), 'wb') as local_file:
            local_file.write(response.content)
