from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery, ClientQuery
from office365.runtime.client_result import ClientResult
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.basePermissions import BasePermissions
from office365.sharepoint.changeCollection import ChangeCollection
from office365.sharepoint.field_collection import FieldCollection
from office365.sharepoint.file import File
from office365.sharepoint.folder import Folder
from office365.sharepoint.folder_collection import FolderCollection
from office365.sharepoint.group import Group
from office365.sharepoint.group_collection import GroupCollection
from office365.sharepoint.list import List
from office365.sharepoint.list_collection import ListCollection
from office365.sharepoint.securable_object import SecurableObject
from office365.sharepoint.user import User
from office365.sharepoint.user_collection import UserCollection


class Web(SecurableObject):
    """Represents a SharePoint site. A site is a type of SP.SecurableObject.
    Refer this link https://msdn.microsoft.com/en-us/library/office/dn499819.aspx for a details"""

    def __init__(self, context, resource_path=None):
        """

        :type resource_path: ResourcePath or None
        :type context: ClientContext
        """
        if resource_path is None:
            resource_path = ResourcePath("Web")
        super(Web, self).__init__(context, resource_path)
        self._web_url = None

    def get_sub_webs_filtered_for_current_user(self, query):
        """Returns a collection of objects that contain metadata about subsites of the current site (2) in which the
        current user is a member.
        :type query: SubwebQuery"""
        users = UserCollection(self.context)
        qry = ServiceOperationQuery(self, "getSubwebsFilteredForCurrentUser", {
            "nWebTemplateFilter": query.WebTemplateFilter,
            "nConfigurationFilter": query.ConfigurationFilter
        }, None, None, users)
        self.context.add_query(qry)
        return users

    def get_all_webs(self):
        """Returns a collection containing a flat list of all Web objects in the Web object."""
        result = ClientResult(self.webs)
        qry = ClientQuery(self.webs, None, None, result)
        self.context.add_query(qry)
        self.context.afterExecuteOnce += self._load_sub_webs
        return result

    def _load_sub_webs(self, result):
        self._load_sub_webs_inner(result.value)

    def _load_sub_webs_inner(self, webs, result=None):
        if result is None:
            result = webs
        for parent_web in webs:
            sub_webs = parent_web.webs
            self.context.load(sub_webs)
            self.context.execute_query()
            for web in sub_webs:
                result.add_child(web)
            self._load_sub_webs_inner(sub_webs, result)

    def update(self):
        """Update a Web resource"""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Delete a Web resource"""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()

    def get_file_by_server_relative_url(self, url):
        """Returns the file object located at the specified server-relative URL.
        :type url: str
        """
        return File(
            self.context,
            ResourcePathServiceOperation("getFileByServerRelativeUrl", [url], self.resource_path)
        )

    def get_folder_by_server_relative_url(self, url):
        """Returns the folder object located at the specified server-relative URL.
        :type url: str
        """
        return Folder(
            self.context,
            ResourcePathServiceOperation("getFolderByServerRelativeUrl", [url], self.resource_path)
        )

    def ensure_user(self, login_name):
        """Checks whether the specified logon name belongs to a valid user of the website, and if the logon name does
        not already exist, adds it to the website.
        :type login_name: str
        """
        target_user = User(self.context)
        self.siteUsers.add_child(target_user)
        qry = ServiceOperationQuery(self, "ensureUser", [login_name], None, None, target_user)
        self.context.add_query(qry)
        return target_user

    def get_user_effective_permissions(self, user_name):
        """Gets the effective permissions that the specified user has within the current application scope.
        :type user_name: str
        """
        result = ClientResult(BasePermissions())
        qry = ServiceOperationQuery(self, "GetUserEffectivePermissions", [user_name], None, None, result)
        self.context.add_query(qry)
        return result

    def does_user_have_permissions(self, permission_mask):
        """Returns whether the current user has the given set of permissions.
        :type permission_mask: BasePermissions
        """
        result = ClientResult(bool)
        qry = ServiceOperationQuery(self, "doesUserHavePermissions", [permission_mask], None, None, result)
        self.context.add_query(qry)
        return result

    def get_user_by_id(self, user_id):
        """Returns the user corresponding to the specified member identifier for the current site.
        :type user_id: long
        """
        return User(self.context,
                    ResourcePathServiceOperation("getUserById", [user_id], self.resource_path))

    def get_list(self, url):
        """Get list by url
        :type url: str
        """
        return List(self.context,
                    ResourcePathServiceOperation("getList", [url], self.resource_path))

    def get_changes(self, query):
        """Returns the collection of all changes from the change log that have occurred within the scope of the site,
        based on the specified query.
        :type query: ChangeQuery"""
        changes = ChangeCollection(self.context)
        qry = ServiceOperationQuery(self, "getChanges", None, query, "query", changes)
        self.context.add_query(qry)
        return changes

    @property
    def webs(self):
        """Get child webs"""
        if self.is_property_available('Webs'):
            return self.properties['Webs']
        else:
            from office365.sharepoint.webCollection import WebCollection
            parent_web_url = None
            if self.is_property_available('Url'):
                parent_web_url = self.properties['Url']
            return WebCollection(self.context,
                                 ResourcePath("webs", self.resource_path),
                                 parent_web_url)

    @property
    def folders(self):
        """Get folder resources"""
        if self.is_property_available('Folders'):
            return self.properties['Folders']
        else:
            return FolderCollection(self.context, ResourcePath("folders", self.resource_path))

    @property
    def lists(self):
        """Get web list collection"""
        if self.is_property_available('Lists'):
            return self.properties['Lists']
        else:
            return ListCollection(self.context, ResourcePath("lists", self.resource_path))

    @property
    def siteUsers(self):
        """Get site users"""
        if self.is_property_available('SiteUsers'):
            return self.properties['SiteUsers']
        else:
            return UserCollection(self.context, ResourcePath("siteUsers", self.resource_path))

    @property
    def siteGroups(self):
        """Gets the collection of groups for the site collection."""
        if self.is_property_available('SiteGroups'):
            return self.properties['SiteGroups']
        else:
            return GroupCollection(self.context, ResourcePath("siteGroups", self.resource_path))

    @property
    def currentUser(self):
        """Gets the current user."""
        if self.is_property_available('CurrentUser'):
            return self.properties['CurrentUser']
        else:
            return User(self.context, ResourcePath("CurrentUser", self.resource_path))

    @property
    def parentWeb(self):
        """Gets the parent website of the specified website."""
        if self.is_property_available('ParentWeb'):
            return self.properties['ParentWeb']
        else:
            return User(self.context, ResourcePath("ParentWeb", self.resource_path))

    @property
    def associatedVisitorGroup(self):
        """Gets or sets the associated visitor group of the Web site."""
        if self.is_property_available('AssociatedVisitorGroup'):
            return self.properties['AssociatedVisitorGroup']
        else:
            return Group(self.context, ResourcePath("AssociatedVisitorGroup", self.resource_path))

    @property
    def associatedOwnerGroup(self):
        """Gets or sets the associated owner group of the Web site."""
        if self.is_property_available('AssociatedOwnerGroup'):
            return self.properties['AssociatedOwnerGroup']
        else:
            return Group(self.context, ResourcePath("AssociatedOwnerGroup", self.resource_path))

    @property
    def associatedMemberGroup(self):
        """Gets or sets the group of users who have been given contribute permissions to the Web site."""
        if self.is_property_available('AssociatedMemberGroup'):
            return self.properties['AssociatedMemberGroup']
        else:
            return Group(self.context, ResourcePath("AssociatedMemberGroup", self.resource_path))

    @property
    def fields(self):
        """Specifies the collection of all the fields (2) in the site (2)."""
        if self.is_property_available('Fields'):
            return self.properties['Fields']
        else:
            return FieldCollection(self.context, ResourcePath("Fields", self.resource_path))

    @property
    def url(self):
        """Gets the absolute URL for the website."""
        if self.is_property_available('Url'):
            return self.properties['Url']
        else:
            return None

    @property
    def webTemplate(self):
        """Gets the name of the site definition or site template that was used to create the site."""
        if self.is_property_available('WebTemplate'):
            return self.properties['WebTemplate']
        else:
            return None

    def set_property(self, name, value, persist_changes=True):
        super(Web, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "Url":
            self._web_url = value

    @property
    def resource_url(self):
        url = super(Web, self).resource_url
        if self._web_url is not None:
            url = url.replace(self.context.service_root_url, self._web_url + '/_api/')
        return url
