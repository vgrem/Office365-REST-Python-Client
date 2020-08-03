from office365.runtime.client_query import ClientQuery, DeleteEntityQuery, UpdateEntityQuery
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.actions.getWebUrlFromPage import GetWebUrlFromPageUrlQuery
from office365.sharepoint.changes.changeCollection import ChangeCollection
from office365.sharepoint.contenttypes.content_type_collection import ContentTypeCollection
from office365.sharepoint.fields.field_collection import FieldCollection
from office365.sharepoint.files.file import File
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.folders.folder_collection import FolderCollection
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.list_collection import ListCollection
from office365.sharepoint.permissions.basePermissions import BasePermissions
from office365.sharepoint.permissions.roleDefinitionCollection import RoleDefinitionCollection
from office365.sharepoint.permissions.securable_object import SecurableObject
from office365.sharepoint.principal.group import Group
from office365.sharepoint.principal.group_collection import GroupCollection
from office365.sharepoint.principal.user import User
from office365.sharepoint.principal.user_collection import UserCollection
from office365.sharepoint.sharing.externalSharingSiteOption import ExternalSharingSiteOption
from office365.sharepoint.sharing.objectSharingSettings import ObjectSharingSettings
from office365.sharepoint.sharing.sharingResult import SharingResult
from office365.sharepoint.ui.applicationpages.clientPeoplePickerQueryParameters import ClientPeoplePickerQueryParameters
from office365.sharepoint.ui.applicationpages.clientPeoplePickerWebServiceInterface import (
    ClientPeoplePickerWebServiceInterface,
)
from office365.sharepoint.webs.regional_settings import RegionalSettings


class Web(SecurableObject):
    """Represents a SharePoint site. A site is a type of SP.SecurableObject.
    Refer this link https://msdn.microsoft.com/en-us/library/office/dn499819.aspx for a details"""

    def __init__(self, context, resource_path=None):
        """

        :type resource_path: ResourcePath or None
        :type context: office365.sharepoint.client_context.ClientContext
        """
        if resource_path is None:
            resource_path = ResourcePath("Web")
        super(Web, self).__init__(context, resource_path)
        self._web_url = None

    @staticmethod
    def get_web_url_from_page_url(context, page_full_url):
        """Determine whether site exists
        :type context: office365.sharepoint.client_context.ClientContext
        :type page_full_url: str
        """
        qry = GetWebUrlFromPageUrlQuery(context, page_full_url)
        context.add_query(qry)
        return qry.return_type

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

        def _load_sub_webs(resp):
            self._load_sub_webs_inner(result.value)
        self.context.after_execute(_load_sub_webs)
        return result

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

    @staticmethod
    def create_anonymous_link(context, url, is_edit_link):
        """Create an anonymous link which can be used to access a document without needing to authenticate.

        :param bool is_edit_link: If true, the link will allow the guest user edit privileges on the item.
        :param str url: The URL of the site, with the path of the object in SharePoint represented as query
        string parameters
        :param office365.sharepoint.client_context.ClientContext context: client context
        """
        result = ClientResult(bool)
        payload = {
            "url": context.base_url + url,
            "isEditLink": is_edit_link
        }
        qry = ServiceOperationQuery(context.web, "CreateAnonymousLink", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def get_object_sharing_settings(context, object_url, group_id, use_simplified_roles):
        """Given a path to an object in SharePoint, this will generate a sharing settings object which contains
        necessary information for rendering sharing information..

        :param office365.sharepoint.client_context.ClientContext context: SharePoint client
        :param str object_url: A URL with one of two possible formats.
              The two possible URL formats are:
              1) The URL of the site, with the path of the object in SharePoint represented as query string parameters,
              forSharing set to 1 if sharing, and mbypass set to 1 to bypass any mobile logic
              e.g. http://contoso.com/?forSharing=1&mbypass=1&List=%7BCF908473%2D72D4%2D449D%2D8A53%2D4BD01EC54B84%7D&
              obj={CF908473-72D4-449D-8A53-4BD01EC54B84},1,DOCUMENT
              2) The URL of the SharePoint object (web, list, item) intended for sharing
              e.g. http://contoso.com/Documents/SampleFile.docx
        :param int group_id: The id value of the permissions group if adding to a group, 0 otherwise.
        :param bool use_simplified_roles: A Boolean value indicating whether to use the SharePoint
        simplified roles (Edit, View) or not.
        """
        result = ObjectSharingSettings(context)
        payload = {
            "objectUrl": object_url,
            "groupId": group_id,
            "useSimplifiedRoles": use_simplified_roles
        }
        qry = ServiceOperationQuery(context.web, "GetObjectSharingSettings", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

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
        qry = ServiceOperationQuery(self, "doesUserHavePermissions", permission_mask, None, None, result)
        self.context.add_query(qry)
        return result

    def get_folder_by_id(self, unique_id):
        """

        :type unique_id: str
        """
        folder = Folder(self.context)
        qry = ServiceOperationQuery(self, "getFolderById", [unique_id], None, None, folder)
        self.context.add_query(qry)
        return folder

    def get_user_by_id(self, user_id):
        """Returns the user corresponding to the specified member identifier for the current site.

        :param int user_id: Specifies the member identifier.
        """
        return User(self.context,
                    ResourcePathServiceOperation("getUserById", [user_id], self.resource_path))

    def default_document_library(self):
        """Retrieves the default document library."""
        return List(self.context,
                    ResourcePathServiceOperation("defaultDocumentLibrary", None, self.resource_path))

    def get_list(self, url):
        """Get list by url

        :type url: str
        """
        return List(self.context,
                    ResourcePathServiceOperation("getList", [url], self.resource_path))

    def get_changes(self, query):
        """Returns the collection of all changes from the change log that have occurred within the scope of the site,
        based on the specified query.

        :param office365.sharepoint.changeQuery.ChangeQuery query: Specifies which changes to return
        """
        changes = ChangeCollection(self.context)
        qry = ServiceOperationQuery(self, "getChanges", None, query, "query", changes)
        self.context.add_query(qry)
        return changes

    def share(self, user_principal_name,
              shareOption=ExternalSharingSiteOption.View,
              sendEmail=True, emailSubject=None, emailBody=None):
        """
        Share a Web with user

        :param str user_principal_name: User identifier
        :param ExternalSharingSiteOption shareOption: The sharing type of permission to grant on the object.
        :param bool sendEmail: A flag to determine if an email notification SHOULD be sent (if email is configured).
        :param str emailSubject: The email subject.
        :param str emailBody: The email subject.
        :return: SharingResult
        """

        picker_result = ClientResult(str)
        sharing_result = ClientResult(SharingResult(self.context))

        def _picker_value_resolved(picker_value):
            picker_result.value = picker_value

        def _grp_resolved(role_value):
            def _web_loaded():
                sharing_result.value = Web.share_object(self.context, self.url, picker_result.value, role_value,
                                                        0,
                                                        False, sendEmail, False, emailSubject, emailBody)

            self.ensure_property("Url", _web_loaded)

        params = ClientPeoplePickerQueryParameters(user_principal_name)
        ClientPeoplePickerWebServiceInterface.client_people_picker_resolve_user(self.context, params,
                                                                                _picker_value_resolved)
        Web._resolve_group_value(self.context, shareOption, _grp_resolved)
        return sharing_result.value

    def unshare(self):
        """
        Unshare a Web

        :return: SharingResult
        """
        sharing_result = ClientResult(SharingResult(self.context))

        def _web_initialized():
            sharing_result.value = Web.unshare_object(self.context, self.url)
        self.ensure_property("Url", _web_initialized)
        return sharing_result.value

    @staticmethod
    def _resolve_group_value(context, share_option, on_resolved):
        """

        :param office365.sharepoint.client_context.ClientContext context:
        :param ExternalSharingSiteOption share_option:
        :param (str) -> None on_resolved:
        """
        options = {
            ExternalSharingSiteOption.View: context.web.associatedVisitorGroup,
            ExternalSharingSiteOption.Edit: context.web.associatedMemberGroup,
            ExternalSharingSiteOption.Owner: context.web.associatedOwnerGroup,
        }
        grp = options[share_option]
        context.load(grp)

        def _group_resolved(resp):
            role_value = "group:{groupId}".format(groupId=grp.properties["Id"])
            on_resolved(role_value)
        context.after_execute(_group_resolved)

    @staticmethod
    def share_object(context, url, peoplePickerInput,
                     roleValue=None,
                     groupId=0, propagateAcl=False,
                     sendEmail=True, includeAnonymousLinkInEmail=False, emailSubject=None, emailBody=None,
                     useSimplifiedRoles=True):
        """
        This method shares an object in SharePoint such as a list item or site. It returns a SharingResult object
        which contains the completion script and a page to redirect to if desired.


        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param str url: The URL of the website with the path of an object in SharePoint query string parameters.
        :param str roleValue: The sharing role value for the type of permission to grant on the object.
        :param str peoplePickerInput: A string of JSON representing users in people picker format.
        :param int groupId: The ID of the group to be added. Zero if not adding to a permissions group.
        :param bool propagateAcl:  A flag to determine if permissions SHOULD be pushed to items with unique permissions.
        :param bool sendEmail: A flag to determine if an email notification SHOULD be sent (if email is configured).
        :param bool includeAnonymousLinkInEmail: If an email is being sent, this determines if an anonymous link
        SHOULD be added to the message.
        :param str emailSubject: The email subject.
        :param str emailBody: The email subject.
        :param bool useSimplifiedRoles: A Boolean value indicating whether to use the SharePoint simplified roles
        (Edit, View) or not.

        """
        result = SharingResult(context)
        payload = {
            "url": url,
            "groupId": groupId,
            "peoplePickerInput": peoplePickerInput,
            "roleValue": roleValue,
            "includeAnonymousLinkInEmail": includeAnonymousLinkInEmail,
            "propagateAcl": propagateAcl,
            "sendEmail": sendEmail,
            "emailSubject": emailSubject,
            "emailBody": emailBody,
            "useSimplifiedRoles": useSimplifiedRoles
        }
        qry = ServiceOperationQuery(context.web, "ShareObject", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def unshare_object(context, url):
        """
        Removes Sharing permissions on an object.

        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param str url: A SharingResult object which contains status codes pertaining to the completion of the operation
        :return: SharingResult
        """
        result = SharingResult(context)
        payload = {
            "url": url
        }
        qry = ServiceOperationQuery(context.web, "UnshareObject", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    def get_file_by_id(self, unique_id):
        """Returns the file object with the specified GUID.

        :param str unique_id: A GUID that identifies the file object.
        """
        return_file = File(self.context)
        qry = ServiceOperationQuery(self.context.web, "GetFileById", [unique_id], None, None, return_file)
        self.context.add_query(qry)
        return return_file

    def get_list_item(self, str_url):
        """
        Returns the list item that is associated with the specified server-relative URL.

        :param str str_url: A string that contains the server-relative URL,
        for example, "/sites/MySite/Shared Documents/MyDocument.docx".
        :return: ListItem
        """
        return_item = ListItem(self.context, ResourcePathServiceOperation("GetListItem", [str_url], self.resource_path))
        return return_item

    def get_catalog(self, type_catalog):
        """Gets the list template gallery, site template gallery, or Web Part gallery for the Web site.

        :param int type_catalog: The type of the gallery.
        """
        return List(self.context, ResourcePathServiceOperation("getCatalog", [type_catalog], self.resource_path))

    @property
    def webs(self):
        """Get child webs"""
        if self.is_property_available('Webs'):
            return self.properties['Webs']
        else:
            from office365.sharepoint.webs.web_collection import WebCollection
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
    def contentTypes(self):
        """Gets the collection of content types for the Web site."""
        if self.is_property_available('ContentTypes'):
            return self.properties['ContentTypes']
        else:
            return ContentTypeCollection(self.context, ResourcePath("ContentTypes", self.resource_path))

    @property
    def roleDefinitions(self):
        """Gets the collection of role definitions for the Web site."""
        return self.properties.get("RoleDefinitions",
                                   RoleDefinitionCollection(self.context,
                                                            ResourcePath("RoleDefinitions",
                                                                         self.resource_path)))

    @property
    def url(self):
        """Gets the absolute URL for the website."""
        if self.is_property_available('Url'):
            return self.properties['Url']
        else:
            return None

    @property
    def web_template(self):
        """Gets the name of the site definition or site template that was used to create the site."""
        if self.is_property_available('WebTemplate'):
            return self.properties['WebTemplate']
        else:
            return None

    @property
    def regional_settings(self):
        """Gets the regional settings that are currently implemented on the website."""
        if self.is_property_available('RegionalSettings'):
            return self.properties['RegionalSettings']
        else:
            return RegionalSettings(self.context, ResourcePath("RegionalSettings", self.resource_path))

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
