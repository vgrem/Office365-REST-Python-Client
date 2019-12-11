from office365.runtime.client_query import  UpdateEntityQuery, DeleteEntityQuery, ServiceOperationQuery
from office365.runtime.resource_path_entity import ResourcePathEntity
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.utilities.http_method import HttpMethod
from office365.sharepoint.file import File
from office365.sharepoint.folder import Folder
from office365.sharepoint.folder_collection import FolderCollection
from office365.sharepoint.group_collection import GroupCollection
from office365.sharepoint.list_collection import ListCollection
from office365.sharepoint.securable_object import SecurableObject
from office365.sharepoint.user import User
from office365.sharepoint.user_collection import UserCollection


class Web(SecurableObject):
    """Represents a SharePoint site. A site is a type of SP.SecurableObject.
    Refer this link https://msdn.microsoft.com/en-us/library/office/dn499819.aspx for a details"""

    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = ResourcePathEntity(context, None, "Web")
        super(Web, self).__init__(context, resource_path)
        self._web_path = None

    def update(self):
        """Update a Web resource"""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Delete a Web resource"""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        # self.removeFromParentCollection()

    def get_file_by_server_relative_url(self, url):
        """Returns the file object located at the specified server-relative URL."""
        file_obj = File(
            self.context,
            ResourcePathServiceOperation(self.context, self.resourcePath, "getfilebyserverrelativeurl", [url])
        )
        return file_obj

    def get_folder_by_server_relative_url(self, url):
        """Returns the folder object located at the specified server-relative URL."""
        folder_obj = Folder(
            self.context,
            ResourcePathServiceOperation(self.context, self.resourcePath, "getfolderbyserverrelativeurl", [url])
        )
        return folder_obj

    def ensureUser(self, login_name):
        user = User(self.context)
        qry = ServiceOperationQuery(self, HttpMethod.Post, "ensureuser", [login_name])
        self.context.add_query(qry, user)
        return user

    @property
    def webs(self):
        """Get child webs"""
        if self.is_property_available('Webs'):
            return self.properties['Webs']
        else:
            from office365.sharepoint.web_collection import WebCollection
            parent_web_url = None
            if self.is_property_available('Url'):
                parent_web_url = self.properties['Url']
            return WebCollection(self.context,
                                 ResourcePathEntity(self.context, self.resourcePath, "webs"),
                                 parent_web_url)

    @property
    def folders(self):
        """Get folder resources"""
        if self.is_property_available('Folders'):
            return self.properties['Folders']
        else:
            return FolderCollection(self.context, ResourcePathEntity(self.context, self.resourcePath, "folders"))

    @property
    def lists(self):
        """Get web list collection"""
        if self.is_property_available('Lists'):
            return self.properties['Lists']
        else:
            return ListCollection(self.context, ResourcePathEntity(self.context, self.resourcePath, "lists"))

    @property
    def siteUsers(self):
        """Get site users"""
        if self.is_property_available('SiteUsers'):
            return self.properties['SiteUsers']
        else:
            return UserCollection(self.context, ResourcePathEntity(self.context, self.resourcePath, "siteusers"))

    @property
    def siteGroups(self):
        """Gets the collection of groups for the site collection."""
        if self.is_property_available('SiteGroups'):
            return self.properties['SiteGroups']
        else:
            return GroupCollection(self.context, ResourcePathEntity(self.context, self.resourcePath, "sitegroups"))

    @property
    def currentUser(self):
        """Gets the current user."""
        if self.is_property_available('CurrentUser'):
            return self.properties['CurrentUser']
        else:
            return User(self.context, ResourcePathEntity(self.context, self.resourcePath, "CurrentUser"))

    @property
    def parentWeb(self):
        """Gets the parent website of the specified website."""
        if self.is_property_available('ParentWeb'):
            return self.properties['ParentWeb']
        else:
            return User(self.context, ResourcePathEntity(self.context, self.resourcePath, "ParentWeb"))

    @property
    def associatedVisitorGroup(self):
        """Gets or sets the associated visitor group of the Web site."""
        if self.is_property_available('AssociatedVisitorGroup'):
            return self.properties['AssociatedVisitorGroup']
        else:
            return User(self.context, ResourcePathEntity(self.context, self.resourcePath, "AssociatedVisitorGroup"))

    @property
    def associatedOwnerGroup(self):
        """Gets or sets the associated owner group of the Web site."""
        if self.is_property_available('AssociatedOwnerGroup'):
            return self.properties['AssociatedOwnerGroup']
        else:
            return User(self.context, ResourcePathEntity(self.context, self.resourcePath, "AssociatedOwnerGroup"))

    @property
    def associatedMemberGroup(self):
        """Gets or sets the group of users who have been given contribute permissions to the Web site."""
        if self.is_property_available('AssociatedMemberGroup'):
            return self.properties['AssociatedMemberGroup']
        else:
            return User(self.context, ResourcePathEntity(self.context, self.resourcePath, "AssociatedMemberGroup"))

    @property
    def serviceRootUrl(self):
        orig_root_url = super(Web, self).serviceRootUrl
        if self.is_property_available("Url"):
            cur_root_url = self.properties["Url"] + "/_api/"
            return cur_root_url
        return orig_root_url
