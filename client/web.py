import urllib

from client.runtime.client_object import ClientObject
from client.runtime.client_query import ClientQuery
from client.runtime.resource_path_entry import ResourcePathEntry
from client.file import File
from client.folder import Folder
from client.folder_collection import FolderCollection
from client.group_collection import GroupCollection
from client.user import User
from client.user_collection import UserCollection
from list_collection import ListCollection
from web_collection import WebCollection


class Web(ClientObject):
    """Web client object.
    Refer this link https://msdn.microsoft.com/en-us/library/office/dn499819.aspx for a details"""

    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = ResourcePathEntry(context, None, "Web")
        super(Web, self).__init__(context, resource_path)

    def update(self):
        """Update a Web resource"""
        qry = ClientQuery.update_entry_query(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Delete a Web resource"""
        qry = ClientQuery.delete_entry_query(self)
        self.context.add_query(qry)
        # self.removeFromParentCollection()

    def get_file_by_server_relative_url(self, url):
        """Returns the file object located at the specified server-relative URL."""
        enc_url = urllib.urlencode(url)
        file_obj = File(self.context, "getfilebyserverrelativeurl('{0}')".format(enc_url), self.resource_path)
        return file_obj

    def get_folder_by_server_relative_url(self, url):
        """Returns the folder object located at the specified server-relative URL."""
        enc_url = urllib.urlencode(url)
        folder_obj = Folder(self.context, "getfolderbyserverrelativeurl('{0}')".format(enc_url), self.resource_path)
        return folder_obj

    @property
    def webs(self):
        """Get child webs"""
        if self.is_property_available('Webs'):
            return self.properties['Webs']
        else:
            return WebCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "webs"))

    @property
    def folders(self):
        """Get folder resources"""
        if self.is_property_available('Folders'):
            return self.properties['Folders']
        else:
            return FolderCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "folders"))

    @property
    def lists(self):
        """Get web list collection"""
        if self.is_property_available('Lists'):
            return self.properties['Lists']
        else:
            return ListCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "lists"))

    @property
    def site_users(self):
        """Get site users"""
        if self.is_property_available('SiteUsers'):
            return self.properties['SiteUsers']
        else:
            return UserCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "siteusers"))

    @property
    def site_groups(self):
        """Gets the collection of groups for the site collection."""
        if self.is_property_available('SiteGroups'):
            return self.properties['SiteGroups']
        else:
            return GroupCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "sitegroups"))

    @property
    def current_user(self):
        """Gets the current user."""
        if self.is_property_available('CurrentUser'):
            return self.properties['CurrentUser']
        else:
            return User(self.context, ResourcePathEntry(self.context, self.resource_path, "CurrentUser"))
