from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.actions.getWebUrlFromPage import GetWebUrlFromPageUrlQuery
from office365.sharepoint.alerts.alert_collection import AlertCollection
from office365.sharepoint.changes.change_collection import ChangeCollection
from office365.sharepoint.clientsidecomponent.types import SPClientSideComponentQueryResult
from office365.sharepoint.contenttypes.content_type_collection import ContentTypeCollection
from office365.sharepoint.eventreceivers.event_receiver_definition import EventReceiverDefinitionCollection
from office365.sharepoint.fields.field_collection import FieldCollection
from office365.sharepoint.files.file import File
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.folders.folder_collection import FolderCollection
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.document_library_information import DocumentLibraryInformation
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.list_collection import ListCollection
from office365.sharepoint.lists.list_template_collection import ListTemplateCollection
from office365.sharepoint.navigation.navigation import Navigation
from office365.sharepoint.permissions.base_permissions import BasePermissions
from office365.sharepoint.permissions.roleDefinitionCollection import RoleDefinitionCollection
from office365.sharepoint.permissions.securable_object import SecurableObject
from office365.sharepoint.principal.group import Group
from office365.sharepoint.principal.group_collection import GroupCollection
from office365.sharepoint.principal.user import User
from office365.sharepoint.principal.user_collection import UserCollection
from office365.sharepoint.recyclebin.recycleBinItemCollection import RecycleBinItemCollection
from office365.sharepoint.sharing.externalSharingSiteOption import ExternalSharingSiteOption
from office365.sharepoint.sharing.objectSharingSettings import ObjectSharingSettings
from office365.sharepoint.sharing.sharingLinkData import SharingLinkData
from office365.sharepoint.sharing.sharing_result import SharingResult
from office365.sharepoint.sites.site_types import SiteCollectionCorporateCatalogAccessor
from office365.sharepoint.tenant.administration.tenant_types import TenantCorporateCatalogAccessor
from office365.sharepoint.ui.applicationpages.client_people_picker import (
    ClientPeoplePickerWebServiceInterface, ClientPeoplePickerQueryParameters
)
from office365.sharepoint.webparts.client_web_part_collection import ClientWebPartCollection
from office365.sharepoint.webs.regional_settings import RegionalSettings
from office365.sharepoint.webs.web_information_collection import WebInformationCollection
from office365.sharepoint.webs.web_template_collection import WebTemplateCollection


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
        """Gets Web from page url

        :type context: office365.sharepoint.client_context.ClientContext
        :type page_full_url: str
        """
        qry = GetWebUrlFromPageUrlQuery(context, page_full_url)
        context.add_query(qry)
        return qry.return_type

    def get_all_client_side_components(self):
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "getAllClientSideComponents", None, None, None, result)
        self.context.add_query(qry)
        return result

    def get_client_side_web_parts(self, project, includeErrors=False):
        result = ClientValueCollection(SPClientSideComponentQueryResult)
        params = {
            "includeErrors": includeErrors,
            "project": project
        }
        qry = ServiceOperationQuery(self, "getClientSideWebParts", None, params, None, result)
        self.context.add_query(qry)
        return result

    def add_supported_ui_language(self, lcid):
        qry = ServiceOperationQuery(self, "getSubWebsFilteredForCurrentUser", {"lcid": lcid}, None, None, None)
        self.context.add_query(qry)
        return self

    def get_sub_webs_filtered_for_current_user(self, query):
        """Returns a collection of objects that contain metadata about subsites of the current site (2) in which the
        current user is a member.

        :type query: office365.sharepoint.webs.subweb_query.SubwebQuery
        """
        users = WebInformationCollection(self.context)
        qry = ServiceOperationQuery(self, "getSubWebsFilteredForCurrentUser", {
            "nWebTemplateFilter": query.WebTemplateFilter,
            "nConfigurationFilter": query.ConfigurationFilter
        }, None, None, users)
        self.context.add_query(qry)
        return users

    def get_recycle_bin_items(self, pagingInfo=None, rowLimit=100, isAscending=True, orderBy=None, itemState=None):
        """

        :param str pagingInfo:
        :param int rowLimit:
        :param bool isAscending:
        :param orderBy: int
        :param int itemState:
        """
        result = RecycleBinItemCollection(self.context)
        payload = {
            "rowLimit": rowLimit,
            "isAscending": isAscending
        }
        qry = ServiceOperationQuery(self, "GetRecycleBinItems", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def get_all_webs(self):
        """Returns a collection containing a flat list of all Web objects in the Web object."""
        result = ClientResult(self.context, self.webs)
        qry = ClientQuery(self.context, self.webs, None, None, result)
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

    def get_list_using_path(self, decoded_url):
        return_list = List(self.context)
        self.lists.add_child(return_list)
        from office365.sharepoint.types.resource_path import ResourcePath as SPResPath
        qry = ServiceOperationQuery(self, "GetListUsingPath", SPResPath(decoded_url), None, None, return_list)
        self.context.add_query(qry)
        return return_list

    def get_regional_datetime_schema(self):
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "GetRegionalDateTimeSchema", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_sharing_link_data(self, linkUrl):
        result = SharingLinkData()
        qry = ServiceOperationQuery(self, "GetSharingLinkData", [linkUrl], None, None, result)
        self.context.add_query(qry)
        return result

    @staticmethod
    def get_context_web_theme_data(context):
        """

        :type context: office365.sharepoint.client_context.ClientContext
        """
        result = ClientResult(context)
        qry = ServiceOperationQuery(context.web, "GetContextWebThemeData", None, None, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def create_anonymous_link(context, url, is_edit_link):
        """Create an anonymous link which can be used to access a document without needing to authenticate.

        :param bool is_edit_link: If true, the link will allow the guest user edit privileges on the item.
        :param str url: The URL of the site, with the path of the object in SharePoint represented as query
        string parameters
        :param office365.sharepoint.client_context.ClientContext context: client context
        """
        result = ClientResult(context)
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

    def ensure_folder_path(self, path):
        """
        Ensures a nested folder hierarchy exist

        :param str path: relative server URL (path) to a folder
        """
        return self.root_folder.folders.ensure_folder_path(path)

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
        result = ClientResult(self.context, BasePermissions())
        qry = ServiceOperationQuery(self, "GetUserEffectivePermissions", [user_name], None, None, result)
        self.context.add_query(qry)
        return result

    def does_user_have_permissions(self, permission_mask):
        """Returns whether the current user has the given set of permissions.

        :type permission_mask: BasePermissions
        """
        result = ClientResult(self.context)
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

        :param office365.sharepoint.changes.change_query.ChangeQuery query: Specifies which changes to return
        """
        changes = ChangeCollection(self.context)
        qry = ServiceOperationQuery(self, "getChanges", None, query, "query", changes)
        self.context.add_query(qry)
        return changes

    def get_available_web_templates(self, lcid=1033, doIncludeCrossLanguage=False):
        """
        Returns a collection of site templates available for the site.

        :param int lcid: Specifies the LCID of the site templates to be retrieved.
        :param bool doIncludeCrossLanguage: Specifies whether to include language-neutral site templates.
        :return:
        """
        params = {
            "lcid": lcid,
            "doIncludeCrossLanguage": doIncludeCrossLanguage
        }
        return_type = WebTemplateCollection(self.context,
                                            ResourcePathServiceOperation("GetAvailableWebTemplates ", params,
                                                                         self.resource_path))

        qry = ServiceOperationQuery(self, "GetAvailableWebTemplates", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def apply_web_template(self, webTemplate):
        """
        Applies the specified site definition or site template to the website that has no template applied to it.

        :param str webTemplate: The name of the site definition or the file name of the site template to be applied.
        :return:
        """
        qry = ServiceOperationQuery(self, "ApplyWebTemplate", {"webTemplate": webTemplate})
        self.context.add_query(qry)
        return self

    def get_custom_list_templates(self):
        """
        Specifies the collection of custom list templates for a given site.

        """
        return_type = ListTemplateCollection(self.context)
        qry = ServiceOperationQuery(self, "GetCustomListTemplates", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_by_guest_url(self, guestUrl):
        """
        :type guestUrl: str
        """
        return_type = File(self.context)
        qry = ServiceOperationQuery(self, "GetFileByGuestUrl", [guestUrl], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_folder_by_guest_url(self, guestUrl):
        """
        :type guestUrl: str
        """
        return_type = File(self.context)
        qry = ServiceOperationQuery(self, "GetFolderByGuestUrl", [guestUrl], None, None, return_type)
        self.context.add_query(qry)
        return return_type

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

        picker_result = ClientResult(self.context)
        sharing_result = ClientResult(self.context, SharingResult(self.context))

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
        result = ClientResult(self.context)

        def _web_initialized():
            result.value = Web.unshare_object(self.context, self.url)
        self.ensure_property("Url", _web_initialized)
        return result.value

    @staticmethod
    def get_document_libraries(context, web_full_url):
        """
        Returns the document libraries of a SharePoint site, specifically a list of objects that represents
        document library information. Document libraries that are private—picture library, catalog library,
        asset library, application list, form template or libraries—for whom the user does not have permission to view
        the items are not included.

        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param str web_full_url: The URL of the web.
        """
        result = ClientValueCollection(DocumentLibraryInformation)
        payload = {
            "webFullUrl": web_full_url
        }
        qry = ServiceOperationQuery(context.web, "GetDocumentLibraries", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def get_document_and_media_libraries(context, web_full_url, include_page_libraries):
        """

        :param context:
        :param str web_full_url:
        :param bool include_page_libraries:
        """
        result = ClientValueCollection(DocumentLibraryInformation)
        payload = {
            "webFullUrl": web_full_url,
            "includePageLibraries": include_page_libraries
        }
        qry = ServiceOperationQuery(context.web, "GetDocumentAndMediaLibraries", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

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
    def get_sharing_link_kind(context, fileUrl):
        """

        :param office365.sharepoint.client_context.ClientContext context:
        :param str fileUrl:
        """
        result = ClientResult(context)
        qry = ServiceOperationQuery(context.web, "GetSharingLinkKind", None, {"fileUrl": fileUrl}, None, result)
        qry.static = True
        context.add_query(qry)
        return result

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
                                 ResourcePath("webs", self.resource_path), parent_web_url)

    @property
    def folders(self):
        """Get folder resources"""
        return self.properties.get('Folders',
                                   FolderCollection(self.context, ResourcePath("folders", self.resource_path)))

    @property
    def lists(self):
        """Get web list collection"""
        return self.properties.get('Lists',
                                   ListCollection(self.context, ResourcePath("lists", self.resource_path)))

    @property
    def siteUsers(self):
        """Get site users"""
        return self.properties.get('SiteUsers',
                                   UserCollection(self.context, ResourcePath("siteUsers", self.resource_path)))

    @property
    def siteGroups(self):
        """Gets the collection of groups for the site collection."""
        return self.properties.get('SiteGroups',
                                   GroupCollection(self.context, ResourcePath("siteGroups", self.resource_path)))

    @property
    def current_user(self):
        """Gets the current user."""
        return self.properties.get('CurrentUser',
                                   User(self.context, ResourcePath("CurrentUser", self.resource_path)))

    @property
    def parentWeb(self):
        """Gets the parent website of the specified website."""
        return self.properties.get('ParentWeb',
                                   Web(self.context, ResourcePath("ParentWeb", self.resource_path)))

    @property
    def associatedVisitorGroup(self):
        """Gets or sets the associated visitor group of the Web site."""
        return self.properties.get('AssociatedVisitorGroup',
                                   Group(self.context, ResourcePath("AssociatedVisitorGroup", self.resource_path)))

    @property
    def associatedOwnerGroup(self):
        """Gets or sets the associated owner group of the Web site."""
        return self.properties.get('AssociatedOwnerGroup',
                                   Group(self.context, ResourcePath("AssociatedOwnerGroup", self.resource_path)))

    @property
    def associatedMemberGroup(self):
        """Gets or sets the group of users who have been given contribute permissions to the Web site."""
        return self.properties.get('AssociatedMemberGroup',
                                   Group(self.context, ResourcePath("AssociatedMemberGroup", self.resource_path)))

    @property
    def fields(self):
        """Specifies the collection of all the fields (2) in the site (2)."""
        return self.properties.get('Fields',
                                   FieldCollection(self.context, ResourcePath("Fields", self.resource_path)))

    @property
    def content_types(self):
        """Gets the collection of content types for the Web site."""
        return self.properties.get('ContentTypes',
                                   ContentTypeCollection(self.context,
                                                         ResourcePath("ContentTypes", self.resource_path)))

    @property
    def role_definitions(self):
        """Gets the collection of role definitions for the Web site."""
        return self.properties.get("RoleDefinitions",
                                   RoleDefinitionCollection(self.context,
                                                            ResourcePath("RoleDefinitions",
                                                                         self.resource_path)))

    @property
    def event_receivers(self):
        """Get Event receivers"""
        return self.properties.get('EventReceivers',
                                   EventReceiverDefinitionCollection(self.context,
                                                                     ResourcePath("eventReceivers", self.resource_path),
                                                                     self))

    @property
    def client_web_parts(self):
        """Client Web Parts"""
        return self.properties.get('ClientWebParts',
                                   ClientWebPartCollection(self.context,
                                                           ResourcePath("ClientWebParts", self.resource_path)))

    @property
    def tenant_app_catalog(self):
        return self.properties.get('TenantAppCatalog',
                                   TenantCorporateCatalogAccessor(self.context,
                                                                  ResourcePath("TenantAppCatalog", self.resource_path)))

    @property
    def site_collection_app_catalog(self):
        return self.properties.get('SiteCollectionAppCatalog',
                                   SiteCollectionCorporateCatalogAccessor(self.context,
                                                                          ResourcePath("SiteCollectionAppCatalog",
                                                                                       self.resource_path)))

    @property
    def url(self):
        """Gets the absolute URL for the website.
        :rtype: str or None
        """
        return self.properties.get('Url', None)

    @property
    def quick_launch_enabled(self):
        """Gets a value that specifies whether the Quick Launch area is enabled on the site.
        :rtype: bool or None
        """
        return self.properties.get('QuickLaunchEnabled', None)

    @quick_launch_enabled.setter
    def quick_launch_enabled(self, value):
        """Sets a value that specifies whether the Quick Launch area is enabled on the site.
        :type value: bool
        """
        self.set_property('QuickLaunchEnabled', value)

    @property
    def site_logo_url(self):
        """Gets a value that specifies Site logo url.
        :rtype: str or None
        """
        return self.properties.get('SiteLogoUrl', None)

    @property
    def list_templates(self):
        """Gets a value that specifies the collection of list definitions and list templates available for creating
            lists on the site."""
        return self.properties.get('ListTemplates',
                                   ListTemplateCollection(self.context,
                                                          ResourcePath("ListTemplates", self.resource_path)))

    @property
    def web_template(self):
        """Gets the name of the site definition or site template that was used to create the site.
        :rtype: str or None
        """
        return self.properties.get('WebTemplate', None)

    @property
    def regional_settings(self):
        """Gets the regional settings that are currently implemented on the website."""
        return self.properties.get('RegionalSettings',
                                   RegionalSettings(self.context, ResourcePath("RegionalSettings", self.resource_path)))

    @property
    def recycle_bin(self):
        """Get recycle bin"""
        return self.properties.get('RecycleBin',
                                   RecycleBinItemCollection(self.context,
                                                            ResourcePath("RecycleBin", self.resource_path)))

    @property
    def navigation(self):
        """Gets a web site navigation."""
        return self.properties.get('Navigation',
                                   Navigation(self.context,
                                              ResourcePath("Navigation", self.resource_path)))

    @property
    def root_folder(self):
        """Get a root folder"""
        return self.properties.get("RootFolder", Folder(self.context, ResourcePath("RootFolder", self.resource_path)))

    @property
    def alerts(self):
        return self.properties.get('Alerts',
                                   AlertCollection(self.context,
                                                   ResourcePath("Alerts", self.resource_path)))

    @property
    def available_fields(self):
        return self.properties.get('AvailableFields',
                                   FieldCollection(self.context,
                                                   ResourcePath("AvailableFields", self.resource_path)))

    @property
    def welcome_page(self):
        return self.properties.get('WelcomePage', None)

    @property
    def supported_ui_language_ids(self):
        """Specifies the language code identifiers (LCIDs) of the languages that are enabled for the site."""
        return self.properties.get('SupportedUILanguageIds', ClientValueCollection(int))

    @property
    def ui_version(self):
        """
        Gets or sets the user interface (UI) version of the Web site.
        :rtype: int or None
        """
        return self.properties.get('UIVersion', None)

    def get_property(self, name):
        if name == "ContentTypes":
            return self.content_types
        elif name == "RootFolder":
            return self.root_folder
        elif name == "RegionalSettings":
            return self.regional_settings
        elif name == "RoleDefinitions":
            return self.role_definitions
        elif name == "RecycleBin":
            return self.recycle_bin
        elif name == "CurrentUser":
            return self.current_user
        elif name == "AvailableFields":
            return self.available_fields
        else:
            return super(Web, self).get_property(name)

    def set_property(self, name, value, persist_changes=True):
        super(Web, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "Url":
            self._web_url = value
        return self

    @property
    def resource_url(self):
        url = super(Web, self).resource_url
        if self._web_url is not None:
            url = url.replace(self.context.service_root_url(), self._web_url + '/_api/')
        return url
