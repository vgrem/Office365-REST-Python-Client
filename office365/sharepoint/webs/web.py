# coding=utf-8
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Callable, Optional, Union
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.operations import Progress
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata
from office365.sharepoint.activities.entity import SPActivityEntity
from office365.sharepoint.activities.logger import ActivityLogger
from office365.sharepoint.alerts.collection import AlertCollection
from office365.sharepoint.authentication.acs_service_principal_info import (
    SPACSServicePrincipalInfo,
)
from office365.sharepoint.businessdata.app_bdc_catalog import AppBdcCatalog
from office365.sharepoint.changes.collection import ChangeCollection
from office365.sharepoint.changes.query import ChangeQuery
from office365.sharepoint.clientsidecomponent.hostedapps.manager import (
    HostedAppsManager,
)
from office365.sharepoint.clientsidecomponent.identifier import (
    SPClientSideComponentIdentifier,
)
from office365.sharepoint.clientsidecomponent.query_result import (
    SPClientSideComponentQueryResult,
)
from office365.sharepoint.clientsidecomponent.storage_entity import StorageEntity
from office365.sharepoint.contenttypes.collection import ContentTypeCollection
from office365.sharepoint.contenttypes.content_type import ContentType
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.eventreceivers.definition_collection import (
    EventReceiverDefinitionCollection,
)
from office365.sharepoint.features.collection import FeatureCollection
from office365.sharepoint.fields.collection import FieldCollection
from office365.sharepoint.fields.datetime_field_format_type import (
    DateTimeFieldFormatType,
)
from office365.sharepoint.files.file import File
from office365.sharepoint.flows.synchronization_result import FlowSynchronizationResult
from office365.sharepoint.folders.collection import FolderCollection
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.internal.paths.web import WebPath
from office365.sharepoint.largeoperation.operation import SPLargeOperation
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.collection import ListCollection
from office365.sharepoint.lists.document_library_information import (
    DocumentLibraryInformation,
)
from office365.sharepoint.lists.get_parameters import GetListsParameters
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.render_data_parameters import RenderListDataParameters
from office365.sharepoint.lists.templates.collection import ListTemplateCollection
from office365.sharepoint.lists.templates.type import ListTemplateType
from office365.sharepoint.marketplace.corporatecuratedgallery.addins.principals_response import (
    SPGetAddinPrincipalsResponse,
)
from office365.sharepoint.marketplace.corporatecuratedgallery.available_addins_response import (
    SPAvailableAddinsResponse,
)
from office365.sharepoint.marketplace.sitecollection.appcatalog.accessor import (
    SiteCollectionCorporateCatalogAccessor,
)
from office365.sharepoint.marketplace.tenant.appcatalog.accessor import (
    TenantCorporateCatalogAccessor,
)
from office365.sharepoint.navigation.navigation import Navigation
from office365.sharepoint.permissions.base_permissions import BasePermissions
from office365.sharepoint.permissions.roles.definitions.collection import (
    RoleDefinitionCollection,
)
from office365.sharepoint.permissions.securable_object import SecurableObject
from office365.sharepoint.principal.groups.collection import GroupCollection
from office365.sharepoint.principal.groups.group import Group
from office365.sharepoint.principal.users.collection import UserCollection
from office365.sharepoint.principal.users.user import User
from office365.sharepoint.pushnotifications.collection import (
    PushNotificationSubscriberCollection,
)
from office365.sharepoint.pushnotifications.subscriber import PushNotificationSubscriber
from office365.sharepoint.recyclebin.item_collection import RecycleBinItemCollection
from office365.sharepoint.sharing.external_site_option import ExternalSharingSiteOption
from office365.sharepoint.sharing.links.access_request import SharingLinkAccessRequest
from office365.sharepoint.sharing.links.data import SharingLinkData
from office365.sharepoint.sharing.object_sharing_settings import ObjectSharingSettings
from office365.sharepoint.sharing.result import SharingResult
from office365.sharepoint.sharing.shared_document_info import SharedDocumentInfo
from office365.sharepoint.sitescripts.serialization_info import (
    SiteScriptSerializationInfo,
)
from office365.sharepoint.sitescripts.serialization_result import (
    SiteScriptSerializationResult,
)
from office365.sharepoint.sitescripts.utility import SiteScriptUtility
from office365.sharepoint.translation.resource_entry import SPResourceEntry
from office365.sharepoint.translation.user_resource import UserResource
from office365.sharepoint.types.property_values import PropertyValues
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath
from office365.sharepoint.ui.applicationpages.peoplepicker.web_service_interface import (
    ClientPeoplePickerWebServiceInterface,
)
from office365.sharepoint.usercustomactions.collection import UserCustomActionCollection
from office365.sharepoint.views.view import View
from office365.sharepoint.webparts.client.collection import ClientWebPartCollection
from office365.sharepoint.webs.calendar_type import CalendarType
from office365.sharepoint.webs.collection import WebCollection
from office365.sharepoint.webs.context_web_information import ContextWebInformation
from office365.sharepoint.webs.dataleakage_prevention_status_info import (
    SPDataLeakagePreventionStatusInfo,
)
from office365.sharepoint.webs.information_collection import WebInformationCollection
from office365.sharepoint.webs.modernize_homepage_result import ModernizeHomepageResult
from office365.sharepoint.webs.multilingual_settings import MultilingualSettings
from office365.sharepoint.webs.regional_settings import RegionalSettings
from office365.sharepoint.webs.subweb_query import SubwebQuery
from office365.sharepoint.webs.templates.collection import WebTemplateCollection
from office365.sharepoint.webs.theme_info import ThemeInfo

if TYPE_CHECKING:
    from office365.sharepoint.changes.token import ChangeToken
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.clientsidecomponent.spteamsappcomponent import (
        SPTeamsAppComponent,
    )
    from office365.sharepoint.documents.fontoption import FontOption
    from office365.sharepoint.folders.coloring import FolderColoring
    from office365.sharepoint.marketplace.corporatecuratedgallery.addins.permission_request import (
        SPAddinPermissionRequest,
    )
    from office365.sharepoint.marketplace.corporatecuratedgallery.addins.permission_response import (
        SPAddinPermissionResponse,
    )
    from office365.sharepoint.marketplace.corporatecuratedgallery.carddesigns.card_designs import (
        CardDesigns,
    )
    from office365.sharepoint.marketplace.corporatecuratedgallery.spuninstalladdinjobdetail import (
        SPUninstallAddinJobDetail,
    )
    from office365.sharepoint.marketplace.corporatecuratedgallery.spuninstalladdinrequest import (
        SPUninstallAddinRequest,
    )
    from office365.sharepoint.marketplace.corporatecuratedgallery.spuninstalladdinresponse import (
        SPUninstallAddinResponse,
    )
    from office365.sharepoint.publishing.pages.page import SitePage
    from office365.sharepoint.webs.apptile import AppTile
    from office365.sharepoint.webs.sp_focal_point import SPFocalPoint
    from office365.sharepoint.webs.spimageitem import SPImageItem
    from office365.sharepoint.workflow.associations.association import (
        WorkflowAssociation,
    )
    from office365.sharepoint.workflow.template import WorkflowTemplate


class Web(SecurableObject):
    """
    Represents a SharePoint site. A site is a type of SecurableObject.

    A group of related webpages that is hosted by a server on the World Wide Web or an intranet.
    Each website has its own entry points, metadata, administration settings, and workflows.
    Also referred to as web site.
    """

    def __init__(self, context: ClientContext, resource_path: Optional[ResourcePath] = None):
        """ """
        if resource_path is None:
            resource_path = WebPath("Web")
        super().__init__(context, resource_path)
        self._web_url = None

    def __str__(self):
        return self.title or self.entity_type_name

    def available_addins(self, server_relative_urls: Optional[list[str]] = None):
        """Args:
        server_relative_urls (list[str]):
        """
        payload = {"serverRelativeUrls": server_relative_urls}
        return_type = ClientResult(self.context, SPAvailableAddinsResponse())
        qry = ServiceOperationQuery(self, "AvailableAddins", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_cross_farm_message(self, message: str) -> ClientResult[bool]:
        """Args:
        message (str):
        """
        payload = {"messagePayloadBase64": message}
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "AddCrossFarmMessage", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_access_request_list(self) -> List:
        """ """
        return_type = List(self.context)
        self.lists.add_child(return_type)

        def _get_access_request_list():
            return_type.set_property("Url", self.access_request_list_url)

        self.ensure_properties(["AccessRequestListUrl"]).after_execute(lambda _: _get_access_request_list())
        return return_type

    def get_adaptive_card_extensions(self, include_errors: Optional[bool] = None, project=None):
        payload = {
            "includeErrors": include_errors,
            "project": project,
        }
        return_type = ClientResult(self.context, ClientValueCollection(SPClientSideComponentQueryResult))
        qry = ServiceOperationQuery(self, "GetAdaptiveCardExtensions", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_document_by_doc_id(self, doc_id: str) -> ClientResult[str]:
        """ """
        return_type = ClientResult(self.context, str())
        qry = ClientQuery(self.context, return_type=return_type)

        def _construct_request(request: RequestOptions):
            request.url = f"{self.context.base_url}/_layouts/15/DocIdRedir.aspx?ID={doc_id}"

        self.context.add_query(qry).before_execute(_construct_request)
        return return_type

    def get_site_script(
        self,
        include_branding: bool = True,
        included_lists: Optional[list[str]] = None,
        include_links_to_exported_items: bool = True,
        include_regional_settings: bool = True,
    ) -> ClientResult[SiteScriptSerializationResult]:
        """Creates site script syntax from current SharePoint site.

        Args:
            include_branding (bool): Extracts the configuration of the site's branding.
            included_lists (list[str] or None): A list of one or more lists. Each is identified by the list url.
            include_links_to_exported_items (bool): Extracts navigation links. In order to export navigation
                links pointing to lists, the list needs to be included in the request as well.
            include_regional_settings (bool): Extracts the site's regional settings.
        """
        result = ClientResult(self.context, SiteScriptSerializationResult())
        info = SiteScriptSerializationInfo(
            IncludeBranding=include_branding,
            IncludedLists=StringCollection(included_lists) if included_lists else None,
            IncludeLinksToExportedItems=include_links_to_exported_items,
            IncludeRegionalSettings=include_regional_settings,
        )

        def _get_site_script(web_url: str | None):
            assert web_url is not None
            SiteScriptUtility.get_site_script_from_web(self.context, web_url, info, return_type=result)

        self.ensure_property("Url").after_execute(lambda _: _get_site_script(self.url))
        return result

    def consent_to_power_platform(self) -> FlowSynchronizationResult:
        """"""
        return_type = FlowSynchronizationResult(self.context)
        qry = ServiceOperationQuery(self, "ConsentToPowerPlatform", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_list_data_as_stream(self, path: str, view_xml: Optional[str] = None) -> ClientResult[bytes]:
        """Returns list data from the specified list url and for the specified query parameters.

        Args:
            path (str): A string that contains the site-relative URL for a list, for example, /Lists/Announcements.
            view_xml (str):
        """
        if view_xml is None:
            view_xml = "<View><Query></Query></View>"
        return_type = ClientResult(self.context, bytes())

        def _get_list_data_as_stream():
            assert self.url is not None
            list_abs_url = self.url + path
            parameters = RenderListDataParameters(ViewXml=view_xml)
            List.get_list_data_as_stream(self.context, list_abs_url, parameters, return_type=return_type)

        self.ensure_property("Url").after_execute(lambda _: _get_list_data_as_stream())
        return return_type

    def get_onedrive_list_data_as_stream(
        self, view_xml: Optional[Union[str, RenderListDataParameters]] = None
    ) -> ClientResult[bytes]:
        """Returns list data from the specified list url and for the specified query parameters.

        Args:
            view_xml (str):
        """
        if view_xml is None:
            view_xml = RenderListDataParameters()
            view_xml.ViewXml = "<View><Query></Query></View>"
        return List.get_onedrive_list_data_as_stream(self.context, view_xml)  # type: ignore[arg-type]

    def get_list_operation(self, list_id: str, operation_id: str) -> SPLargeOperation:
        """ """
        return_type = SPLargeOperation(self.context)
        qry = ServiceOperationQuery(
            self,
            "GetListOperation",
            None,
            {"listId": list_id, "operationId": operation_id},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_push_notification_subscriber(self, device_app_instance_id: str) -> PushNotificationSubscriber:
        """Specifies the push notification subscriber over the site for the specified device app instance identifier.

        Args:
            device_app_instance_id (str): Device application instance identifier.
        """
        return_type = PushNotificationSubscriber(self.context)
        qry = ServiceOperationQuery(
            self,
            "GetPushNotificationSubscriber",
            [device_app_instance_id],
            None,
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_client_side_components(
        self, components: ClientValueCollection[SPClientSideComponentIdentifier]
    ) -> ClientResult[ClientValueCollection[SPClientSideComponentIdentifier]]:
        """Returns the client side components for the requested components.
        Client components include data necessary to render Client Side Web Parts and Client Side Applications.

        Args:
            components (list): array of requested components, defined by id and version.
        """
        return_type = ClientResult(self.context, ClientValueCollection(SPClientSideComponentIdentifier))
        payload = {"components": components}
        qry = ServiceOperationQuery(self, "GetClientSideComponents", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_client_side_components_by_component_type(self, component_types):
        """Args:
        component_types (str):
        """
        return_type = ClientResult(self.context, ClientValueCollection(SPClientSideComponentIdentifier))
        payload = {"componentTypesString": component_types}
        qry = ServiceOperationQuery(
            self,
            "GetClientSideComponentsByComponentType",
            None,
            payload,
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_push_notification_subscribers_by_user(self, user: Union[str, User]) -> PushNotificationSubscriberCollection:
        """Queries for the push notification subscribers for the site  for the specified user.

        Args:
            user (str or User): User object or login name
        """
        return_type = PushNotificationSubscriberCollection(self.context)

        def _create_and_add_query(login_name: str | None):
            assert login_name is not None
            qry = ServiceOperationQuery(
                self,
                "GetPushNotificationSubscribersByUser",
                [login_name],
                None,
                None,
                return_type,
            )
            self.context.add_query(qry)

        if isinstance(user, User):
            user.ensure_property("LoginName").after_execute(lambda _: _create_and_add_query(user.login_name))
        else:
            _create_and_add_query(user)
        return return_type

    @staticmethod
    def create_organization_sharing_link(
        context: ClientContext, url: str, is_edit_link: bool = False
    ) -> ClientResult[str]:
        """Creates and returns an organization-internal link that can be used to access a document and gain permissions
        to it.

        Args:
            context (office365.sharepoint.client_context.ClientContext):
            url (str): he URL of the site, with the path of the object in SharePoint that is represented as query
                string parameters, forSharing set to 1 if sharing, and bypass set to 1 to bypass any mobile logic.
            is_edit_link (bool): If true, the link will allow the logged in user to edit privileges on the item.
        """
        return_type = ClientResult(context, str())
        params = {"url": url, "isEditLink": is_edit_link}
        qry = ServiceOperationQuery(
            context.web,
            "CreateOrganizationSharingLink",
            None,
            params,
            None,
            return_type,
        )
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def destroy_organization_sharing_link(
        context: ClientContext,
        url: str,
        is_edit_link: bool,
        remove_associated_sharing_link_group: bool,
    ):
        """Removes an existing organization link for an object.

        Args:
            context (office365.sharepoint.client_context.ClientContext): SharePoint client context
            url (str): the URL of the site, with the path of the object in SharePoint that is represented as query string
            parameters, forSharing set to 1 if sharing, and bypass set to 1 to bypass any mobile logic.
            is_edit_link (bool): If true, the link will allow the logged in user to edit privileges on the item.
            remove_associated_sharing_link_group (bool): Indicates whether to remove the groups that contain the users
            who have been given access to the shared object via the sharing link
        """
        payload = {
            "url": url,
            "isEditLink": is_edit_link,
            "removeAssociatedSharingLinkGroup": remove_associated_sharing_link_group,
        }
        qry = ServiceOperationQuery(context.web, "DestroyOrganizationSharingLink", None, payload, None, None)
        qry.static = True
        context.add_query(qry)
        return context.web

    @staticmethod
    def get_context_web_information(
        context: ClientContext,
    ) -> ClientResult[ContextWebInformation]:
        """Returns an object that specifies metadata about the site

        Args:
            context (office365.sharepoint.client_context.ClientContext):
        """
        return_type = ClientResult(context, ContextWebInformation())
        qry = ServiceOperationQuery(context.web, "GetContextWebInformation", None, None, None, return_type, True)
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_web_url_from_page_url(context, page_full_url) -> ClientResult[str]:
        """Returns the URL of the root folder for the site containing the specified URL

        Args:
            context (office365.sharepoint.client_context.ClientContext):
            page_full_url (str): Specifies the URL from which to return the site URL.
        """
        return_type = ClientResult(context, str())
        payload = {"pageFullUrl": page_full_url}
        qry = ServiceOperationQuery(context.web, "GetWebUrlFromPageUrl", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    def create_default_associated_groups(self, user_login: str, user_login2: str, group_name_seed: str):
        """Creates the default Owners, Members and Visitors SPGroups on the web.

        Args:
            user_login (str): The user logon name of the group owner.
            user_login2 (str): The secondary contact for the group.
            group_name_seed (str): The name seed to use when creating of the full names of the default groups.
                For example, if the name seed is Contoso then the default groups will be created with the names:
                Contoso Owners, Contoso Members and Contoso Visitors. If the value of this parameter is null then
                the web title is used instead.
        """
        payload = {
            "userLogin": user_login,
            "userLogin2": user_login2,
            "groupNameSeed": group_name_seed,
        }
        qry = ServiceOperationQuery(self, "CreateDefaultAssociatedGroups", None, payload)
        qry.static = True
        self.context.add_query(qry)
        return self

    def create_group_based_environment(self) -> FlowSynchronizationResult:
        return_type = FlowSynchronizationResult(self.context)
        qry = ServiceOperationQuery(self, "CreateGroupBasedEnvironment", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_group_based_environment(self) -> FlowSynchronizationResult:
        return_type = FlowSynchronizationResult(self.context)
        qry = ServiceOperationQuery(self, "GetGroupBasedEnvironment", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_acs_service_principals(self, app_ids=None):
        """List service principals

        Args:
            app_ids (list[str]):
        """
        payload = {"appIds": app_ids}
        return_type = ClientResult(self.context, ClientValueCollection(SPACSServicePrincipalInfo))
        qry = ServiceOperationQuery(self, "GetACSServicePrincipals", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def sync_flow_instances(self, target_web_url: str) -> FlowSynchronizationResult:
        """Args:
        target_web_url (str):
        """
        return_type = FlowSynchronizationResult(self.context)
        payload = {"targetWebUrl": target_web_url}
        qry = ServiceOperationQuery(self, "SyncFlowInstances", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def sync_flow_templates(self, category: str) -> FlowSynchronizationResult:
        """Args:
        category (str):
        """
        return_type = FlowSynchronizationResult(self.context)
        payload = {"category": category}
        qry = ServiceOperationQuery(self, "SyncFlowTemplates", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_all_client_side_components(self) -> ClientResult[str]:
        """"""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetAllClientSideComponents", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_addin_principals_having_permissions_in_sites(
        self, server_relative_urls: Optional[list[str]] = None, urls: Optional[list[str]] = None
    ) -> ClientResult[SPGetAddinPrincipalsResponse]:
        """Args:
        server_relative_urls (list[str]):
        urls (list[str]):
        """
        payload = {"serverRelativeUrls": server_relative_urls, "urls": urls}
        return_type = ClientResult(self.context, SPGetAddinPrincipalsResponse())
        qry = ServiceOperationQuery(
            self,
            "GetAddinPrincipalsHavingPermissionsInSites",
            None,
            payload,
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_app_bdc_catalog(self) -> AppBdcCatalog:
        """
        Returns the Business Data Connectivity (BDC) MetadataCatalog for an application that gives access to the
        external content types defined in the BDC metadata model packaged by the application.<151>
        This method SHOULD be called on the Web (section 3.2.5.143) object that represents the site for the application
        and it returns the BDC MetadataCatalog deployed on the site.
        """
        return_type = AppBdcCatalog(self.context)
        qry = ServiceOperationQuery(self, "GetAppBdcCatalog", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_client_side_web_parts(self, project=None, include_errors=False):
        """It MUST return an array of 3rd party webpart components installed on this site

        Args:
            include_errors (bool): If true, webparts with errors MUST be included in the results of the request.
                If false, webparts with errors MUST be excluded in the results of the request.
            project (str):
        """
        return_type = ClientResult(self.context, ClientValueCollection(SPClientSideComponentQueryResult))
        params = {"includeErrors": include_errors, "project": project}
        qry = ServiceOperationQuery(self, "GetClientSideWebParts", None, params, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_supported_ui_language(self, lcid: int) -> Self:
        """Adds a supported UI language by its language identifier.

        Args:
            lcid (int): Specifies the language identifier to be added.
        """
        qry = ServiceOperationQuery(self, "AddSupportedUILanguage", {"lcid": lcid})
        self.context.add_query(qry)
        return self

    def get_lists(self, row_limit: int = 100) -> ListCollection:
        """Args:
        row_limit (int): Specifies a limit for the number of lists in the query that are returned per page
        """
        return_type = ListCollection(self.context)
        payload = {"getListsParams": GetListsParameters(RowLimit=row_limit)}
        qry = ServiceOperationQuery(self, "GetLists", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_sub_webs_filtered_for_current_user(self, query: SubwebQuery) -> WebInformationCollection:
        """Returns a collection of objects that contain metadata about subsites of the current site (2) in which the
        current user is a member.

        Args:
            query (office365.sharepoint.webs.subweb_query.SubwebQuery):
        """
        return_type = WebInformationCollection(self.context)
        qry = ServiceOperationQuery(
            self,
            "getSubWebsFilteredForCurrentUser",
            {
                "nWebTemplateFilter": query.WebTemplateFilter,
                "nConfigurationFilter": query.ConfigurationFilter,
            },
            None,
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_recycle_bin_items(
        self,
        paging_info: Optional[str] = None,
        row_limit: int = 100,
        is_ascending: bool = True,
        order_by: Optional[int] = None,
        item_state: Optional[int] = None,
    ) -> RecycleBinItemCollection:
        """Gets the recycle bin items that are based on the specified query.

        Args:
            paging_info (str): an Object that is used to obtain the next set of rows in a paged view of the Recycle Bin
            row_limit (int): a limit for the number of items returned in the query per page.
            is_ascending (bool): a Boolean value that specifies whether to sort in ascending order.
            order_by (int): the column by which to order the Recycle Bin query.
            item_state (int): Recycle Bin stage of items to return in the query.
        """
        assert self.recycle_bin.resource_path is not None
        return_type = RecycleBinItemCollection(self.context, self.recycle_bin.resource_path)
        payload = {
            "rowLimit": row_limit,
            "isAscending": is_ascending,
            "pagingInfo": paging_info,
            "orderBy": order_by,
            "itemState": item_state,
        }
        qry = ServiceOperationQuery(self, "GetRecycleBinItems", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_recycle_bin_items_by_query_info(
        self,
        is_ascending: bool = True,
        item_state: Optional[int] = None,
        order_by: Optional[int] = None,
        paging_info: Optional[str] = None,
        row_limit: int = 100,
        show_only_my_items: bool = False,
    ) -> RecycleBinItemCollection:
        """Gets the recycle bin items that are based on the specified query.

        Args:
            paging_info (str): an Object that is used to obtain the next set of rows in a paged view of the Recycle Bin
            row_limit (int): a limit for the number of items returned in the query per page.
            is_ascending (bool): a Boolean value that specifies whether to sort in ascending order.
            order_by (int): the column by which to order the Recycle Bin query.
            item_state (int): Recycle Bin stage of items to return in the query.
            show_only_my_items (bool):
        """
        assert self.recycle_bin.resource_path is not None
        return_type = RecycleBinItemCollection(self.context, self.recycle_bin.resource_path)
        payload = {
            "rowLimit": row_limit,
            "isAscending": is_ascending,
            "pagingInfo": paging_info,
            "orderBy": order_by,
            "itemState": item_state,
            "ShowOnlyMyItems": show_only_my_items,
        }
        qry = ServiceOperationQuery(self, "GetRecycleBinItemsByQueryInfo", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_all_webs(self, progress: Optional[Callable[[Progress[Web]], None]] = None) -> WebCollection:
        """Returns a collection containing a flat list of all Web objects in the Web.

        Args:
            progress: Optional hook invoked per web with a ``Progress[Web]``
              snapshot (``done`` = webs discovered so far).
        """

        assert self.webs.resource_path is not None
        return_type = WebCollection(self.context, self.webs.resource_path, self)

        def _webs_loaded():
            self._load_sub_webs_inner(self.webs, return_type, progress)

        self.ensure_property("Webs").after_execute(lambda _: _webs_loaded())
        return return_type

    def _load_sub_webs_inner(
        self, webs: WebCollection, all_webs: WebCollection, progress: Optional[Callable[[Progress[Web]], None]] = None
    ):
        for cur_web in webs:
            all_webs.add_child(cur_web)
            if callable(progress):
                progress(Progress(done=len(all_webs), stage="scanning"))

            def _webs_loaded(web):
                if len(web.webs) > 0:
                    self._load_sub_webs_inner(web.webs, all_webs, progress)

            cur_web.ensure_property("Webs").after_execute(lambda _, w=cur_web: _webs_loaded(w))

    def get_list_using_path(self, decoded_url: str):
        """Returns the list that is associated with the specified server-relative path.

        Args:
            decoded_url (str): Contains the site-relative path for a list, for example, /Lists/Announcements.
        """
        path = SPResPath.create_relative(self.context.base_url, decoded_url)
        return_type = List(self.context)
        self.lists.add_child(return_type)
        qry = ServiceOperationQuery(self, "GetListUsingPath", path, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_news_list(self, allow_create: bool = False) -> List:
        """Returns the News List on this web, if it exists. If the list does not exist, the list will be created and
        then returned if allowCreate is set to true. The News List is a hidden SP.List in which News Posts are stored.

        Args:
            allow_create (bool): Indicates whether to create the list if it does not exist on this web. "true" means yes.
        """
        return_type = List(self.context)
        self.lists.add_child(return_type)
        payload = {"allowCreate": allow_create}
        qry = ServiceOperationQuery(self, "GetNewsList", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_view_from_url(self, list_url: str) -> View:
        """Returns a view of a list within the site based on the specified URL.

        Args:
            list_url (str): Contains either an absolute URL or a site-relative URL of a view.
        """
        return View(
            self.context,
            ServiceOperationPath("GetViewFromUrl", [list_url], self.resource_path),
        )

    def get_view_from_path(self, decoded_url: str) -> View:
        """Returns a view of a list within the site based on the specified path.

        Args:
            decoded_url (str): Contains either an absolute path or a site-relative path of a view.
        """
        return View(
            self.context,
            ServiceOperationPath("GetViewFromPath", [decoded_url], self.resource_path),
        )

    def get_regional_datetime_schema(self) -> ClientResult[str]:
        """Get DateTime Schema based on regional settings"""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetRegionalDateTimeSchema", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_sharing_link_data(self, link_url: str) -> ClientResult[SharingLinkData]:
        """This method determines basic information about the supplied link URL, including limited data about the object
        the link URL refers to and any additional sharing link data if the link URL is a tokenized sharing link

        Args:
            link_url (str): A URL that is either a tokenized sharing link or a canonical URL for a document
        """
        return_type = ClientResult(self.context, SharingLinkData())
        payload = {"linkUrl": link_url}
        qry = ServiceOperationQuery(self, "GetSharingLinkData", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def get_context_web_theme_data(context: ClientContext) -> ClientResult[str]:
        """
        Get ThemeData for the context web.
        """
        return_type = ClientResult(context, str())
        qry = ServiceOperationQuery(context.web, "GetContextWebThemeData", None, None, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    def create_site_page(self, page_metadata: str) -> ClientResult[str]:
        """Create a site page

        Args:
            page_metadata (str):
        """
        payload = {"pageMetaData": page_metadata}
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "CreateSitePage", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_site_page(self, name: str, title: str | None = None, page_layout_type: str = "Article") -> "SitePage":
        """Adds a modern site page to this web's Site Pages library.

        The page is created as a draft; execute the returned query and then set the
        page content (``CanvasContent1``) through the item. The ``sitepages``
        endpoint is hosted per web, so a web reached through a subweb context
        creates the page in that subweb.

        Args:
            name: The page file name, e.g. ``Home.aspx``.
            title: The page title; defaults to the file name.
            page_layout_type: ``Article`` (default) or ``SingleWebPartAppPage``.
        """
        from office365.sharepoint.publishing.pages.collection import SitePageCollection

        collection = SitePageCollection(self.context, ResourcePath("sitepages/pages"))
        return collection.add(name=name, title=title, page_layout_type=page_layout_type)

    def get_site_page_by_id(self, page_id: int) -> "SitePage":
        """A modern site page addressed by its list item identifier.

        The returned handle supports page-level operations such as
        :meth:`~office365.sharepoint.publishing.pages.page.SitePage.publish`.

        Args:
            page_id: The ``Id`` of the page in the Site Pages library.
        """
        from office365.sharepoint.publishing.pages.page import SitePage

        return SitePage(self.context, ResourcePath(f"sitepages/pages({page_id})"))

    @staticmethod
    def create_anonymous_link(
        context: ClientContext,
        url: str,
        is_edit_link: bool,
        return_type: Optional[ClientResult[str]] = None,
    ):
        """Create an anonymous link which can be used to access a document without needing to authenticate.

        Args:
            is_edit_link (bool): If true, the link will allow the guest user edit privileges on the item.
            url (str): The URL of the site, with the path of the object in SharePoint represented as query string
                parameters
            context (office365.sharepoint.client_context.ClientContext): client context
            return_type (ClientResult[str]): Return type
        """
        if return_type is None:
            return_type = ClientResult(context, str())
        payload = {
            "url": str(SPResPath.create_absolute(context.base_url, url)),
            "isEditLink": is_edit_link,
        }
        qry = ServiceOperationQuery(context.web, "CreateAnonymousLink", None, payload, None, return_type, True)
        context.add_query(qry)
        return return_type

    @staticmethod
    def create_anonymous_link_with_expiration(
        context: ClientContext,
        url: str,
        is_edit_link: bool,
        expiration_string: str,
        return_type: Optional[ClientResult[str]] = None,
    ):
        """Creates and returns an anonymous link that can be used to access a document without needing to authenticate.

        Args:
            is_edit_link (bool): If true, the link will allow the guest user edit privileges on the item.
            url (str): The URL of the site, with the path of the object in SharePoint represented as query string
                parameters
            expiration_string (str): A date/time string for which the format conforms to the ISO 8601:2004(E) complete
            representation for calendar date and time of day, and which represents the time and date of expiry for the
            anonymous link. Both the minutes and hour value MUST be specified for the difference between the local
                and UTC time.
            Midnight is represented as 00:00:00.
            context (office365.sharepoint.client_context.ClientContext): client context
            return_type (ClientResult): Return type
        """
        if return_type is None:
            return_type = ClientResult(context, str())
        payload = {
            "url": str(SPResPath.create_absolute(context.base_url, url)),
            "isEditLink": is_edit_link,
            "expirationString": expiration_string,
        }
        qry = ServiceOperationQuery(
            context.web,
            "CreateAnonymousLinkWithExpiration",
            None,
            payload,
            None,
            return_type,
        )
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_object_sharing_settings(
        context: ClientContext,
        object_url: str,
        group_id: Optional[str] = None,
        use_simplified_roles: Optional[bool] = None,
        return_type=None,
    ) -> ObjectSharingSettings:
        """Given a path to an object in SharePoint, this will generate a sharing settings object which contains
        necessary information for rendering sharing information

        Args:
            context (office365.sharepoint.client_context.ClientContext): SharePoint client
            object_url (str): A URL with one of two possible formats. The two possible URL formats are: 1) The URL
            of the site, with the path of the object in SharePoint represented as query string parameters,
            forSharing set to 1 if sharing, and mbypass set to 1 to bypass any mobile logic e.g.
            https://contoso.com/?forSharing=1&mbypass=1&List=%7BCF908473%2D72D4%2D449D%2D8A53%2D4BD01EC54B84%7D&
            obj={CF908473-72D4-449D-8A53-4BD01EC54B84},1,DOCUMENT 2) The URL of the SharePoint object
            (web, list, item) intended for sharing e.g. https://contoso.com/Documents/SampleFile.docx
            group_id (int): The id value of the permissions group if adding to a group, 0 otherwise.
            use_simplified_roles (bool): A Boolean value indicating whether to use the SharePoint simplified
            roles (Edit, View) or not.
            return_type (ObjectSharingSettings): Return type
        """
        if return_type is None:
            return_type = ObjectSharingSettings(context)
        payload = {
            "objectUrl": object_url,
            "groupId": group_id,
            "useSimplifiedRoles": use_simplified_roles,
        }
        qry = ServiceOperationQuery(context.web, "GetObjectSharingSettings", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    def get_client_side_components_by_id(self, component_ids: Optional[list[str]] = None):
        """Returns the client side components for the requested component identifiers.
        Client components include data necessary to render Client Side Web Parts and Client Side Applications.

        Args:
            component_ids (list[str]): List of requested component identifiers.
        """
        return_type = ClientResult(self.context, ClientValueCollection(SPClientSideComponentQueryResult))
        payload = {"componentIds": StringCollection(component_ids or [])}
        qry = ServiceOperationQuery(self, "GetClientSideComponentsById", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_by_server_relative_url(self, server_relative_url: str) -> File:
        """Returns the file object located at the specified server-relative URL, for example:
        - "/sites/MySite/Shared Documents/MyDocument.docx"
        - "Shared Documents/MyDocument.docx"

        Args:
            server_relative_url (str): Specifies the server-relative URL for the file.
        """
        path = SPResPath.create_relative(self.context.base_url, server_relative_url)
        return File(
            self.context,
            ServiceOperationPath("getFileByServerRelativeUrl", [str(path)], self.resource_path),
            self.root_folder.files,
        )

    def get_file_by_server_relative_path(self, path: str) -> File:
        """Returns the file object located at the specified server-relative path, for example:
        - "/sites/MySite/Shared Documents/MyDocument.docx"
        - "Shared Documents/MyDocument.docx"
        Note: prefer this method over get_folder_by_server_relative_url since it supports % and # symbols in names

        Args:
            path (str): Contains the server-relative path of the file.
        """
        res_path = SPResPath.create_relative(self.context.base_url, path)
        return File(
            self.context,
            ServiceOperationPath("getFileByServerRelativePath", res_path.to_json(), self.resource_path),
            self.root_folder.files,
        )

    def get_folder_by_server_relative_url(self, url: str) -> Folder:
        """Returns the folder object located at the specified server-relative URL.

        Args:
            url (str): Specifies the server-relative URL for the folder.
        """
        return Folder(
            self.context,
            ServiceOperationPath("getFolderByServerRelativeUrl", [url], self.resource_path),
            self.folders,
        )

    def get_folder_by_server_relative_path(self, decoded_url: str) -> Folder:
        """Returns the folder object located at the specified server-relative URL, for example:
        - "/sites/MySite/Shared Documents"
        - "Shared Documents"
        Prefer this method over get_folder_by_server_relative_url since it supports % and # symbols

        Args:
            decoded_url (str): Contains the server-relative URL for the folder
        """
        path = SPResPath(decoded_url)
        return Folder(
            self.context,
            ServiceOperationPath("getFolderByServerRelativePath", path.to_json(), self.resource_path),
            self.folders,
        )

    def get_site_page_copy_to_status(self, work_item_id):
        """Args:
        work_item_id (str):
        """
        return_type = ClientResult(self.context, str())
        payload = {"workItemId": work_item_id}
        qry = ServiceOperationQuery(self, "GetSitePageCopyToStatus", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_page_move_status(self, work_item_id):
        """Args:
        work_item_id (str):
        """
        return_type = ClientResult(self.context, str())
        payload = {"workItemId": work_item_id}
        qry = ServiceOperationQuery(self, "GetSitePageMoveStatus", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def ensure_folder_path(self, path) -> Folder:
        """Ensures a nested folder hierarchy exist

        Args:
            path (str): relative server URL (path) to a folder
        """
        return self.root_folder.folders.ensure_by_path(path)

    def ensure_content_type(
        self, name: str, description: Optional[str] = None, group: Optional[str] = None
    ) -> ContentType:
        """Ensure a content type with the given name exists (idempotent).

        Args:
            name (str): Content type name
            description (str): Content type description
            group (str): Content type group
        """
        return self.content_types.ensure(name, description, group)

    def ensure_list(
        self,
        title: str,
        description: Optional[str] = None,
        template_type: ListTemplateType = ListTemplateType.GenericList,
    ) -> List:
        """Ensure a list with the given title exists (idempotent).

        Creates the list when a list with the given title doesn't exist; otherwise
        returns the existing list.

        Args:
            title (str): Specifies the display name of the list.
            description (str or None): Specifies the description of the list.
            template_type (ListTemplateType): Specifies the list server template of the list.
        """
        return self.lists.ensure_list(title, description, template_type)

    def ensure_edu_class_setup(self, bypass_for_automation):
        """Args:
        bypass_for_automation (bool):
        """
        return_type = ClientResult(self.context, bool())
        payload = {"byPassForAutomation": bypass_for_automation}
        qry = ServiceOperationQuery(self, "EnsureEduClassSetup", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def ensure_user(self, login_name: str) -> User:
        """Checks whether the specified logon name belongs to a valid user of the website, and if the logon name does
        not already exist, adds it to the website.

        Args:
            login_name (str): Specifies a string that contains the login name.
        """
        return_type = User(self.context)
        self.site_users.add_child(return_type)
        qry = ServiceOperationQuery(self, "EnsureUser", [login_name], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def ensure_tenant_app_catalog(self, caller_id):
        """Args:
        caller_id (str):
        """
        return_type = ClientResult(self.context, bool())
        payload = {"callerId": caller_id}
        qry = ServiceOperationQuery(self, "EnsureTenantAppCatalog", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_list_by_title(self, title):
        """Returns the list with the specified display name.

        Args:
            title (str): Specifies the display name
        """
        return List(
            self.context,
            ServiceOperationPath("GetListByTitle", [title], self.resource_path),
        )

    def does_user_have_permissions(self, permission_mask: BasePermissions) -> ClientResult[bool]:
        """Returns whether the current user has the given set of permissions.

        Args:
            permission_mask (BasePermissions): Specifies the set of permissions to verify.
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "DoesUserHavePermissions", permission_mask, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def does_push_notification_subscriber_exist(self, device_app_instance_id: str):
        """Specifies whether the push notification subscriber exists for the current user
        with the given device  app instance identifier.

        Args:
            device_app_instance_id (str): Device application instance identifier.
        """
        return_type = ClientResult(self.context, bool())
        params = {"deviceAppInstanceId": device_app_instance_id}
        qry = ServiceOperationQuery(self, "DoesPushNotificationSubscriberExist", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_folder_by_id(self, unique_id: str) -> Folder:
        """Returns the folder object with the specified GUID.

        Args:
            unique_id (str): A GUID that identifies the folder.
        """
        return Folder(
            self.context,
            ServiceOperationPath("GetFolderById", [unique_id], self.resource_path),
        )

    def get_user_by_id(self, user_id: int) -> User:
        """Returns the user corresponding to the specified member identifier for the current site.

        Args:
            user_id (int): Specifies the member identifier.
        """
        return User(
            self.context,
            ServiceOperationPath("getUserById", [user_id], self.resource_path),
        )

    def default_document_library(self) -> List:
        """Retrieves the default document library."""
        return List(
            self.context,
            ServiceOperationPath("defaultDocumentLibrary", None, self.resource_path),
        )

    def get_list(self, path: str) -> List:
        """Get list by path

        Args:
            path (str): A string that contains the site-relative URL for a list, for example, /Lists/Announcements.
        """
        safe_path = SPResPath.create_relative(self.context.base_url, path)
        return List(
            self.context,
            ServiceOperationPath("getList", [str(safe_path)], self.resource_path),
        )

    def get_changes(self, query: Optional[ChangeQuery] = None) -> ChangeCollection:
        """Returns the collection of all changes from the change log that have occurred within the scope of the web,
        based on the specified query.

        Args:
            query (office365.sharepoint.changes.query.ChangeQuery): Specifies which changes to return
        """
        if query is None:
            query = ChangeQuery(Web=True, FetchLimit="100")
        return_type = ChangeCollection(self.context)
        payload = {"query": query}
        qry = ServiceOperationQuery(self, "getChanges", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_available_web_templates(self, lcid=1033, do_include_cross_language=False):
        """Returns a collection of site templates available for the site.

        Args:
            lcid (int): Specifies the LCID of the site templates to be retrieved.
            do_include_cross_language (bool): Specifies whether to include language-neutral site templates.
        """
        params = {"lcid": lcid, "doIncludeCrossLanguage": do_include_cross_language}
        return_type = WebTemplateCollection(
            self.context,
            ServiceOperationPath("GetAvailableWebTemplates", params, self.resource_path),
        )

        qry = ServiceOperationQuery(self, "GetAvailableWebTemplates", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def hub_site_data(self, force_refresh: bool = False) -> ClientResult[str]:
        """Retrieves data describing a SharePoint hub site.

        Args:
            force_refresh (bool): Default value is false. When false, the data is returned from the server's cache.
                When true, the cache is refreshed with the latest updates and then returned. Use this if you just made
                changes and need to see those changes right away.
        """
        return_type = ClientResult(self.context, str())
        payload = {"forceRefresh": force_refresh}
        qry = ServiceOperationQuery(self, "HubSiteData", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def increment_site_client_tag(self) -> Self:
        """Increments the client cache control number for this site collection."""
        qry = ServiceOperationQuery(self, "IncrementSiteClientTag")
        self.context.add_query(qry)
        return self

    def apply_web_template(self, web_template: str) -> Self:
        """Applies the specified site definition or site template to the website that has no template applied to it.

        Args:
            web_template (str): The name of the site definition or the file name of the site template to be applied.
        """
        qry = ServiceOperationQuery(self, "ApplyWebTemplate", {"webTemplate": web_template})
        self.context.add_query(qry)
        return self

    def get_custom_list_templates(self) -> ListTemplateCollection:
        """Specifies the collection of custom list templates for a given site."""
        return_type = ListTemplateCollection(self.context)
        qry = ServiceOperationQuery(self, "GetCustomListTemplates", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_by_guest_url(self, guest_url: str) -> File:
        """Returns the file object from the guest access URL.

        Args:
            guest_url (str): The guest access URL to get the file with.
        """
        return_type = File(self.context)
        payload = {"guestUrl": guest_url}
        qry = ServiceOperationQuery(self, "GetFileByGuestUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_by_guest_url_extended(
        self, guest_url: str, ensure_access: bool | None = None, password: str | None = None
    ) -> File:
        """Returns the file object from the tokenized sharing link URL.

        Args:
            guest_url (str): The tokenized sharing link URL for the folder.
            password (str): This value contains the password to be supplied to a tokenized sharing link for
            validation. This value is only needed if the link requires a password before granting access
            and the calling user does not currently have perpetual access through the tokenized sharing link.
            This value MUST be set to the correct password for the tokenized sharing link for the access
            granting operation to succeed. If the tokenized sharing link does not require a password
            or the calling user already has perpetual access through the tokenized sharing link, this
            value will be ignored.
            ensure_access (bool): Indicates if the request to the tokenized sharing link grants
            perpetual access to the calling user.
        """
        return_type = File(self.context)
        payload = {
            "guestUrl": guest_url,
            "requestSettings": SharingLinkAccessRequest(ensure_access, password),
        }
        qry = ServiceOperationQuery(self, "GetFileByGuestUrlExtended", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_by_guest_url_ensure_access(self, guest_url, ensure_access):
        """Returns the file object from the tokenized sharing link URL.

        Args:
            guest_url (str): The guest access URL to get the file with.
            ensure_access (bool): Indicates if the request to the tokenized sharing link grants perpetual access
                to the calling user. If it is set to true then the user who is requesting the file will be granted
                perpetual permissions through the tokenized sharing link.
        """
        return_type = File(self.context)
        payload = {"guestUrl": guest_url, "ensureAccess": ensure_access}
        qry = ServiceOperationQuery(self, "GetFileByGuestUrlEnsureAccess", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_by_linking_url(self, linking_url):
        """Returns the file object from the linking URL.

        Args:
            linking_url (str): The linking URL to return the file object for. A linking URL
            can be obtained from LinkingUrl.
        """
        return_type = File(self.context)
        payload = {"linkingUrl": linking_url}
        qry = ServiceOperationQuery(self, "GetFileByLinkingUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_by_url(self, file_url):
        """Returns the file object from the given URL.

        Args:
            file_url (str): The URL used to get the file object.
        """
        return_type = File(self.context)
        params = {"fileUrl": file_url}
        qry = ServiceOperationQuery(self, "GetFileByUrl", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_by_wopi_frame_url(self, wopi_frame_url: str) -> File:
        """Returns the file object from the WOPI frame URL.

        Args:
            wopi_frame_url (str): The WOPI frame URL used to get the file object.
        """
        return_type = File(self.context)
        qry = ServiceOperationQuery(self, "GetFileByWOPIFrameUrl", [wopi_frame_url], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_folder_by_guest_url(self, guest_url: str) -> Folder:
        """Returns the folder object from the tokenized sharing link URL.

        Args:
            guest_url (str): The tokenized sharing link URL for the folder.
        """
        return_type = Folder(self.context, parent_collection=self.folders)
        payload = {"guestUrl": guest_url}
        qry = ServiceOperationQuery(self, "GetFolderByGuestUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_folder_by_guest_url_extended(self, guest_url, ensure_access=None, password=None):
        """Returns the folder object from the tokenized sharing link URL.

        Args:
            guest_url (str): The tokenized sharing link URL for the folder.
            password (str): This value contains the password to be supplied to a tokenized sharing link for
            validation. This value is only needed if the link requires a password before granting access
            and the calling user does not currently have perpetual access through the tokenized sharing link.
            This value MUST be set to the correct password for the tokenized sharing link for the access
            granting operation to succeed. If the tokenized sharing link does not require a password or
            the calling user already has perpetual access through the tokenized sharing link, this value
            will be ignored.
            ensure_access (bool): Indicates if the request to the tokenized sharing link grants perpetual access
                to the calling user.
        """
        return_type = Folder(self.context, parent_collection=self.folders)
        payload = {
            "guestUrl": guest_url,
            "requestSettings": SharingLinkAccessRequest(ensure_access, password),
        }
        qry = ServiceOperationQuery(self, "GetFolderByGuestUrlExtended", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def parse_datetime(
        self,
        value: str,
        display_format: DateTimeFieldFormatType = DateTimeFieldFormatType.DateTime,
        calendar_type: CalendarType = CalendarType.Unknown,
    ) -> ClientResult[str]:
        """Returns parsed DateTime value.

        Args:
            value (str): The input is the string of a datetime that's in web's local time and in web's calendar.
            For example, the input "09/08/1430" when web's calendar was set to Hijri, the actual datetime
            is 07/31/2009 in Gregorian calendar.
            display_format (int): Int value representing SP.DateTimeFieldFormatType
            calendar_type (int): Int value representing SP.CalendarType
        """
        return_type = ClientResult[str](self.context)
        payload = {
            "value": value,
            "displayFormat": display_format.value,
            "calendarType": calendar_type.value,
        }
        qry = ServiceOperationQuery(self, "ParseDateTime", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def share(
        self,
        user_principal_name: str,
        share_option: ExternalSharingSiteOption = ExternalSharingSiteOption.View,
        send_email: bool = True,
        email_subject: str | None = None,
        email_body: str | None = None,
    ) -> SharingResult:
        """Share a Web with user

        Args:
            user_principal_name (str): User identifier
            share_option (ExternalSharingSiteOption): The sharing type of permission to grant on the object.
            send_email (bool): A flag to determine if an email notification SHOULD be sent (if email is configured).
            email_subject (str): The email subject.
            email_body (str): The email subject.
        """

        return_type = SharingResult(self.context)

        def _share(picker_result: ClientResult[str]) -> None:
            groups: dict[ExternalSharingSiteOption, Group] = {
                ExternalSharingSiteOption.View: self.associated_visitor_group,
                ExternalSharingSiteOption.Edit: self.associated_member_group,
                ExternalSharingSiteOption.Owner: self.associated_owner_group,
            }

            picker_input = f"[{picker_result.value}]"
            role_value = f"group:{groups[share_option].id}"
            assert self.url is not None
            Web.share_object(
                self.context,
                self.url,
                picker_input,
                role_value,
                0,
                False,
                send_email,
                False,
                email_subject,
                email_body,
                return_type=return_type,
            )

        def _web_resolved():
            ClientPeoplePickerWebServiceInterface.client_people_picker_resolve_user(
                self.context, user_principal_name
            ).after_execute(_share)

        self.ensure_properties(
            [
                "Url",
                "AssociatedVisitorGroup",
                "AssociatedMemberGroup",
                "AssociatedOwnerGroup",
            ]
        ).after_execute(lambda _: _web_resolved())
        return return_type

    def unshare(self):
        """Removes Sharing permissions on a Web"""
        return_type = SharingResult(self.context)

        def _web_initialized():
            Web.unshare_object(self.context, self.url, return_type=return_type)

        self.ensure_property("Url").after_execute(lambda _: _web_initialized())
        return return_type

    @staticmethod
    def get_document_libraries(
        context: "ClientContext",
        web_full_url: str,
        return_type: Optional[ClientResult[ClientValueCollection[DocumentLibraryInformation]]] = None,
    ) -> ClientResult[ClientValueCollection[DocumentLibraryInformation]]:
        """
            Returns the document libraries of a SharePoint site, specifically a list of objects that represents
            document library information. Document libraries that are private—picture library, catalog library,
            asset library, application list, form template or libraries—for whom the user does not have permission to
            view the items are not included.

        Args:
            context: Authenticated SharePoint client context
            web_full_url: Absolute URL of the target web (site)
            return_type: Optional return type

        Returns:
            ClientResult containing collection of DocumentLibraryInformation objects

        Example:
            >>> result = Web.get_document_libraries(context, "https://contoso.sharepoint.com/sites/mysite")
            >>> for lib in result.value:
            ...     print(lib.Title, lib.AbsoluteUrl)
        """
        if return_type is None:
            return_type = ClientResult(context, ClientValueCollection(DocumentLibraryInformation))
        payload = {"webFullUrl": web_full_url}
        qry = ServiceOperationQuery(context.web, "GetDocumentLibraries", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    def get_default_document_library_url(
        self,
    ) -> ClientResult[DocumentLibraryInformation]:
        """
        Retrieves the URL of the default document library (typically "Shared Documents")
        as a ClientResult containing DocumentLibraryInformation.

        Returns:
            ClientResult[DocumentLibraryInformation]:
                A result object containing the default document library's information,
                including its URL and other metadata.

        """
        return_type = ClientResult(self.context, DocumentLibraryInformation())

        def _get_default_document_library_url() -> None:
            Web.default_document_library_url(self.context, self.url, return_type)

        self.ensure_property("Url").after_execute(lambda _: _get_default_document_library_url())
        return return_type

    @staticmethod
    def default_document_library_url(context, web_url, return_type=None):
        """Returns the default document library URL.

        Args:
            context (office365.sharepoint.client_context.ClientContext): SharePoint context
            web_url (str): URL of the web.
            return_type: Return type of the returned document
        """
        if return_type is None:
            return_type = ClientResult(context, DocumentLibraryInformation())
        payload = {
            "webUrl": web_url,
        }
        qry = ServiceOperationQuery(
            context.web,
            "DefaultDocumentLibraryUrl",
            None,
            payload,
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def delete_all_anonymous_links_for_object(context: ClientContext, url: str):
        """Removes all existing anonymous links for an object.

        Args:
            context (office365.sharepoint.client_context.ClientContext): SharePoint context
            url (str): The URL of the object being shared, with the path of the object in SharePoint that is
                represented as query string parameters.
        """
        payload = {"url": url}
        qry = ServiceOperationQuery(context.web, "DeleteAllAnonymousLinksForObject", None, payload)
        qry.static = True
        context.add_query(qry)
        return context.web

    @staticmethod
    def delete_anonymous_link_for_object(context, url, is_edit_link, remove_associated_sharing_link_group):
        """Removes an existing anonymous link for an object..

        Args:
            context (office365.sharepoint.client_context.ClientContext): SharePoint context
            url (str): The URL of the object being shared, with the path of the object in SharePoint that is
                represented as query string parameters.
            is_edit_link (bool): If true, the edit link for the object will be removed. If false, the view only
                link for the object will be removed.
            remove_associated_sharing_link_group (bool): Indicates whether to remove the groups that contain the
                users who have been given access to the shared object via the sharing link¹.
        """
        payload = {
            "url": url,
            "isEditLink": is_edit_link,
            "removeAssociatedSharingLinkGroup": remove_associated_sharing_link_group,
        }
        qry = ServiceOperationQuery(context.web, "DeleteAnonymousLinkForObject", None, payload)
        qry.static = True
        context.add_query(qry)
        return context.web

    @staticmethod
    def get_document_and_media_libraries(context, web_full_url, include_page_libraries):
        """Returns the document libraries of a SharePoint site, including picture, asset, and site assets libraries.
        Document libraries that are private, catalog library, application list, form template, or libraries that user
        does not have permission to view items are not inlcuded.

        Args:
            context (office365.sharepoint.client_context.ClientContext): SharePoint context
            web_full_url (str): URL of the web.
            include_page_libraries (bool): Indicates whether to include page libraries. A value of "true" means yes.
        """
        return_type = ClientResult(context, ClientValueCollection(DocumentLibraryInformation))
        payload = {
            "webFullUrl": web_full_url,
            "includePageLibraries": include_page_libraries,
        }
        qry = ServiceOperationQuery(
            context.web,
            "GetDocumentAndMediaLibraries",
            None,
            payload,
            None,
            return_type,
        )
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_sharing_link_kind(
        context: ClientContext,
        file_url: str,
        return_type: Optional[ClientResult[int]] = None,
    ):
        """This method determines the kind of tokenized sharing link represented by the supplied file URL.

        Args:
            context (office365.sharepoint.client_context.ClientContext):
            file_url (str): A URL that is a tokenized sharing link for a document
            return_type (ClientResult or None): Return object
        """
        if return_type is None:
            return_type = ClientResult(context)
        qry = ServiceOperationQuery(
            context.web,
            "GetSharingLinkKind",
            None,
            {"fileUrl": file_url},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def forward_object_link(context, url, people_picker_input, email_subject=None, email_body=None):
        """Shares an object in SharePoint, such as a list item or a site with no Acl changes, by sending the link.
        This is used when the user has no permission to share and cannot send access request.
        The user can use this method to send the link of the object to site members who already have permission
        to view the object.
        Returns a SharingResult object that contains completion script and page for redirection if desired.

        Args:
            context (office365.sharepoint.client_context.ClientContext): SharePoint context
            url (str): The URL of the website with the path of an object in SharePoint query string parameters.
            people_picker_input (str): A string of JSON representing users in people picker format.
            email_subject (str): The email subject.
            email_body (str): The email subject.
        """
        return_type = SharingResult(context)
        payload = {
            "url": url,
            "peoplePickerInput": people_picker_input,
            "emailSubject": email_subject,
            "emailBody": email_body,
        }
        qry = ServiceOperationQuery(context.web, "ForwardObjectLink", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def share_object(
        context: ClientContext,
        url: str,
        people_picker_input: str,
        role_value=None,
        group_id=0,
        propagate_acl=False,
        send_email=True,
        include_anonymous_link_in_email=False,
        email_subject=None,
        email_body=None,
        use_simplified_roles=True,
        return_type=None,
    ):
        """This method shares an object in SharePoint such as a list item or site. It returns a SharingResult object
        which contains the completion script and a page to redirect to if desired.

        Args:
            context (office365.sharepoint.client_context.ClientContext): SharePoint context
            url (str): The URL of the website with the path of an object in SharePoint query string parameters.
            role_value (str): The sharing role value for the type of permission to grant on the object.
            people_picker_input (str): A string of JSON representing users in people picker format.
            group_id (int): The ID of the group to be added. Zero if not adding to a permissions group.
            propagate_acl (bool): A flag to determine if permissions SHOULD be pushed to items with unique permissions
            send_email (bool): A flag to determine if an email notification SHOULD be sent (if email is configured).
            include_anonymous_link_in_email (bool): If an email is being sent, this determines if an anonymous link
                SHOULD be added to the message.
            email_subject (str): The email subject.
            email_body (str): The email subject.
            use_simplified_roles (bool): A Boolean value indicating whether to use the SharePoint simplified
            roles (Edit, View) or not.
            return_type (SharingResult or None): Return type
        """
        if return_type is None:
            return_type = SharingResult(context)
        payload = {
            "url": url,
            "groupId": group_id,
            "peoplePickerInput": people_picker_input,
            "roleValue": role_value,
            "includeAnonymousLinkInEmail": include_anonymous_link_in_email,
            "propagateAcl": propagate_acl,
            "sendEmail": send_email,
            "emailSubject": email_subject,
            "emailBody": email_body,
            "useSimplifiedRoles": use_simplified_roles,
        }
        qry = ServiceOperationQuery(context.web, "ShareObject", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def unshare_object(context, url, return_type=None):
        """Removes Sharing permissions on an object.

        Args:
            context (office365.sharepoint.client_context.ClientContext): SharePoint context
            url (str): A SharingResult object which contains status codes pertaining to the completion of the operation
            return_type (SharingResult): Return type
        """
        if return_type is None:
            return_type = SharingResult(context)
        payload = {"url": url}
        qry = ServiceOperationQuery(context.web, "UnshareObject", None, payload, None, return_type, True)
        context.add_query(qry)
        return return_type

    def get_file_by_id(self, unique_id: str) -> File:
        """Returns the file object with the specified GUID.

        Args:
            unique_id (str): A GUID that identifies the file object.
        """
        return File(
            self.context,
            ServiceOperationPath("GetFileById", [unique_id], self.resource_path),
        )

    def get_list_item(self, str_url: str) -> ListItem:
        """Returns the list item that is associated with the specified server-relative URL.

        Args:
            str_url (str): A string that contains the server-relative URL,
            for example, "/sites/MySite/Shared Documents/MyDocument.docx".
        """
        return ListItem(
            self.context,
            ServiceOperationPath("GetListItem", [str_url], self.resource_path),
        )

    def get_list_item_using_path(self, decoded_url: str) -> ListItem:
        """Returns the list item that is associated with the specified server-relative path.

        Args:
            decoded_url (str): A string that contains the server-relative path,
            for example, "/sites/MySite/Shared Documents/MyDocument.docx"
            or "Shared Documents/MyDocument.docx".
        """
        params = SPResPath.create_relative(self.context.base_url, decoded_url)
        return ListItem(
            self.context,
            ServiceOperationPath("GetListItemUsingPath", params, self.resource_path),
        )

    def get_securable_object(
        self,
        scope: str,
        *,
        list_title: Optional[str] = None,
        url: Optional[str] = None,
    ) -> SecurableObject:
        """Resolves a securable object in this web by ``scope``.

        A single, discoverable entry point for addressing something permissions
        can be assigned to, so callers can write::

            ctx.web.get_securable_object("list", list_title="Documents").grant_access(
                "user@contoso.com", RoleType.Contributor
            ).execute_query()

        Args:
            scope (str): The scope to resolve, case-insensitive:
                ``"web"`` (alias ``"site"``) for the web itself; ``"list"`` for a
                list; ``"folder"`` for a folder; ``"item"`` (alias ``"file"``)
                for a document.
            list_title (str): The display title of the list, required for
                ``scope="list"``.
            url (str): The server-relative URL of the folder or document,
                required for ``scope="folder"`` or ``scope="item"``. Names
                containing ``%`` or ``#`` are supported.

        Returns:
            SecurableObject: The web, the addressed
            :class:`~office365.sharepoint.lists.list.List`, or the
            :class:`~office365.sharepoint.listitems.listitem.ListItem` behind a
            folder/document. Resolution is *deferred* (no request is sent);
            run ``execute_query()`` before reading role assignments.

        Raises:
            ValueError: If ``scope`` is unknown, or the argument required by the
                scope (``list_title`` or ``url``) is missing.
        """
        normalized_scope = scope.strip().lower() if isinstance(scope, str) else ""
        if normalized_scope in ("web", "site"):
            return self
        if normalized_scope == "list":
            if not list_title:
                raise ValueError("list_title is required for scope 'list'")
            return self.lists.get_by_title(list_title)
        if normalized_scope == "folder":
            if not url:
                raise ValueError("url is required for scope 'folder'")
            return self.get_folder_by_server_relative_path(url).list_item_all_fields
        if normalized_scope in ("item", "file"):
            if not url:
                raise ValueError(f"url is required for scope '{normalized_scope}'")
            return self.get_file_by_server_relative_path(url).listItemAllFields
        raise ValueError(f"Unsupported scope: {scope!r}")

    def get_catalog(self, type_catalog: Union[int, ListTemplateType]) -> List:
        """Gets the list template gallery, site template gallery, or Web Part gallery for the Web site.

        Args:
            type_catalog (int): The type of the gallery.
        """
        return List(
            self.context,
            ServiceOperationPath("getCatalog", [int(type_catalog)], self.resource_path),
        )

    def page_context_info(self, include_odb_settings: bool, emit_navigation_info: bool) -> ClientResult[bytes]:
        """Return Page context info for the current list being rendered.

        Args:
            include_odb_settings (bool):
            emit_navigation_info (bool):
        """
        return_type = ClientResult(self.context, bytes())
        payload = {
            "includeODBSettings": include_odb_settings,
            "emitNavigationInfo": emit_navigation_info,
        }
        qry = ServiceOperationQuery(self, "PageContextInfo", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_storage_entity(self, key: str) -> StorageEntity:
        """This will return the storage entity identified by the given key

        Args:
            key (str): ID of storage entity to be returned.
        """
        return_type = StorageEntity(self.context)
        params = {
            "key": key,
        }
        qry = ServiceOperationQuery(self, "GetStorageEntity", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_storage_entity(
        self, key: str, value: str, description: Optional[str] = None, comments: Optional[str] = None
    ):
        """This will set the storage entity identified by the given key

        Args:
            key (str): Id of the storage entity to be set.
            value (str): Value of the storage entity to be set.
            description (str): Description of the storage entity to be set.
            comments (str): Comments of the storage entity to be set.
        """
        payload = {
            "key": key,
            "value": value,
            "description": description,
            "comments": comments,
        }
        qry = ServiceOperationQuery(self, "SetStorageEntity", None, payload, None)
        self.context.add_query(qry)
        return self

    def remove_storage_entity(self, key: str) -> Self:
        """This will remove the storage entity identified by the given key

        Args:
            key (str): Id of the storage entity to be removed.
        """
        params = {
            "key": key,
        }
        qry = ServiceOperationQuery(self, "RemoveStorageEntity", params)
        self.context.add_query(qry)
        return self

    def register_push_notification_subscriber(self, device_app_instance_id: str, service_token: str):
        """Registers the push notification subscriber for the site. If the registration already exists,
        the service token is updated with the new value.

        Args:
            device_app_instance_id (str): Device  app instance identifier.
            service_token (str): Token provided by the notification service to the device to receive notifications.
        """
        payload = {
            "deviceAppInstanceId": device_app_instance_id,
            "serviceToken": service_token,
        }
        return_type = PushNotificationSubscriber(self.context)
        qry = ServiceOperationQuery(self, "RegisterPushNotificationSubscriber", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def unregister_push_notification_subscriber(self, device_app_instance_id: str) -> Self:
        """Unregisters the push notification subscriber from the site

        Args:
            device_app_instance_id (str): Device  app instance identifier.
        """
        payload = {
            "deviceAppInstanceId": device_app_instance_id,
        }
        qry = ServiceOperationQuery(self, "UnregisterPushNotificationSubscriber", None, payload)
        self.context.add_query(qry)
        return self

    def remove_supported_ui_language(self, lcid: str) -> Self:
        """Removes a supported UI language by its language identifier.

        Args:
            lcid (str): Specifies the language identifier to be removed.
        """
        params = {"lcid": lcid}
        qry = ServiceOperationQuery(self, "RemoveSupportedUILanguage", params)
        self.context.add_query(qry)
        return self

    def set_access_request_site_description_and_update(self, description: Optional[str] = None) -> Self:
        """Args:
        description (str):
        """
        payload = {"description": description}
        qry = ServiceOperationQuery(self, "SetAccessRequestSiteDescriptionAndUpdate", None, payload)
        self.context.add_query(qry)
        return self

    def set_global_nav_settings(self, title: str, source: str) -> Self:
        """Args:
        title (str):
        source (str):
        """
        payload = {"title": title, "source": source}
        qry = ServiceOperationQuery(self, "SetGlobalNavSettings", None, payload)
        self.context.add_query(qry)
        return self

    def sync_hub_site_theme(self) -> Self:
        """"""
        qry = ServiceOperationQuery(self, "SyncHubSiteTheme")
        self.context.add_query(qry)
        return self

    def assign_document_id(self, site_prefix, enabled=True):
        """Assign Document IDs

        Args:
            site_prefix (str): Specify whether IDs will be automatically assigned to all documents in the Site
            Collection. Additionally, you can specify a set of 4-12 characters that will be used at the
            beginning of all IDs assigned for documents in this Site Collection, to help ensure that items in
            different Site Collections will never get the same ID. Note: A timer job will be scheduled to assign
            IDs to documents already in the Site Collection.
            enabled (bool):
        """

        props = {
            "docid_x005f_msft_x005f_hier_x005f_siteprefix": site_prefix,
            "docid_x005f_enabled": "1",
        }
        return self.set_property("AllProperties", props).update()

    @property
    def activities(self) -> EntityCollection[SPActivityEntity]:
        return self.properties.get(
            "Activities",
            EntityCollection(
                self.context,
                SPActivityEntity,
                ResourcePath("Activities", self.resource_path),
            ),
        )

    @odata(name="ActivityLogger")
    @property
    def activity_logger(self) -> ActivityLogger:
        """"""
        return self.properties.get(
            "ActivityLogger",
            ActivityLogger(self.context, ResourcePath("ActivityLogger", self.resource_path)),
        )

    @property
    def allow_rss_feeds(self) -> Optional[bool]:
        """
        Gets a Boolean value that specifies whether the site collection allows RSS feeds.
        """
        return self.properties.get("AllowRssFeeds", None)

    @property
    def alternate_css_url(self) -> Optional[str]:
        """Gets the URL for an alternate cascading style sheet (CSS) to use in the website."""
        return self.properties.get("AlternateCssUrl", None)

    @property
    def app_instance_id(self) -> Optional[str]:
        """
        Specifies the identifier of the app instance that this site (2) represents. If this site (2) does not
        represent an app instance, then this MUST specify an empty GUID.
        """
        return self.properties.get("AppInstanceId", None)

    @property
    def author(self) -> User:
        """
        Gets a user object that represents the user who created the Web site.
        """
        return self.properties.get("Author", User(self.context, ResourcePath("Author", self.resource_path)))

    @property
    def created(self) -> datetime:
        """Specifies when the site was created"""
        return self.properties.get("Created", datetime.min)

    @property
    def custom_master_url(self) -> Optional[str]:
        """Gets the URL for a custom master page to apply to the Web site"""
        return self.properties.get("CustomMasterUrl", None)

    @property
    def custom_site_actions_disabled(self) -> Optional[bool]:
        return self.properties.get("CustomSiteActionsDisabled", None)

    @odata(name="DescriptionTranslations")
    @property
    def description_translations(self):
        """"""
        return self.properties.get("DescriptionTranslations", ClientValueCollection(SPResourceEntry))

    @property
    def design_package_id(self) -> Optional[str]:
        """Gets or sets the ID of the Design Package used in this SP.Web.

        A value of Guid.Empty will mean that the default Design Package will be used for this SP.Web.
        The default is determined by the SP.WebTemplate of this SP.Web."""
        return self.properties.get("DesignPackageId", None)

    @property
    def disable_app_views(self) -> Optional[bool]:
        """"""
        return self.properties.get("DisableAppViews", None)

    @property
    def disable_flows(self) -> Optional[bool]:
        """"""
        return self.properties.get("DisableFlows", None)

    @property
    def id(self) -> Optional[str]:
        """Specifies the site identifier for the site"""
        return self.properties.get("Id", None)

    @odata(name="SiteId")
    @property
    def site_id(self) -> Optional[str]:
        """Specifies the site collection identifier for the site collection that contains the site"""
        return self.properties.get("SiteId", None)

    @property
    def language(self) -> Optional[int]:
        """Specifies the language code identifier (LCID) for the language that is used on the site"""
        return self.properties.get("Language", None)

    @odata(name="LastItemModifiedDate")
    @property
    def last_item_modified_date(self) -> Optional[datetime]:
        """Specifies when an item was last modified in the site"""
        return self.properties.get("LastItemModifiedDate", None)

    @odata(name="AccessRequestsList")
    @property
    def access_requests_list(self) -> List:
        """"""
        return self.properties.get(
            "AccessRequestsList",
            List(self.context, ResourcePath("AccessRequestsList", self.resource_path)),
        )

    @property
    def access_request_list_url(self) -> Optional[str]:
        """Gets the URL of the access request list to the current site"""
        return self.properties.get("AccessRequestListUrl", None)

    @property
    def allow_designer_for_current_user(self) -> Optional[bool]:
        """
        Specifies whether the current user is allowed to use a designer application to customize this site
        """
        return self.properties.get("AllowDesignerForCurrentUser", None)

    @property
    def allow_master_page_editing_for_current_user(self) -> Optional[bool]:
        """
        Specifies whether the current user is allowed to edit the master page.
        """
        return self.properties.get("AllowMasterPageEditingForCurrentUser", None)

    @property
    def allow_revert_from_template_for_current_user(self) -> Optional[bool]:
        """
        Specifies whether the current user is allowed to revert the site (2) to a default site template.
        """
        return self.properties.get("AllowRevertFromTemplateForCurrentUser", None)

    @odata(name="EffectiveBasePermissions")
    @property
    def effective_base_permissions(self) -> BasePermissions:
        """Specifies the effective permissions that are assigned to the current user"""
        return self.properties.get("EffectiveBasePermissions", BasePermissions())

    @property
    def enable_minimal_download(self) -> Optional[bool]:
        """
        Specifies whether the site will use the minimal download strategy by default.

        The minimal download strategy will use a single .aspx file (start.aspx) for your pages, with the actual URL
        encoded in the text following the hash mark ('#'). When navigating from page to page, only the changes
        between two compatible pages will be downloaded. Fewer bytes will be downloaded and the page will appear
        more quickly.
        """
        return self.properties.get("EnableMinimalDownload", None)

    @property
    def webs(self) -> WebCollection:
        """Specifies the collection of all child sites for the site"""

        return self.properties.get(
            "Webs",
            WebCollection(self.context, ResourcePath("webs", self.resource_path), self),
        )

    @property
    def folders(self) -> FolderCollection:
        """Specifies the collection of all first-level folders in the site"""
        return self.properties.get(
            "Folders",
            FolderCollection(self.context, ResourcePath("folders", self.resource_path), self),
        )

    @odata(name="HostedApps")
    @property
    def hosted_apps(self) -> HostedAppsManager:
        """"""
        return self.properties.get(
            "HostedApps",
            HostedAppsManager(self.context, ResourcePath("HostedApps", self.resource_path)),
        )

    @property
    def lists(self) -> ListCollection:
        """Specifies the collection of lists that are contained in the site available to the current user based on the
        current user's permissions."""
        return self.properties.get(
            "Lists",
            ListCollection(self.context, ResourcePath("lists", self.resource_path)),
        )

    @odata(name="OneDriveSharedItems")
    @property
    def onedrive_shared_items(self) -> EntityCollection[SharedDocumentInfo]:
        """"""
        return self.properties.get(
            "OneDriveSharedItems",
            EntityCollection(
                self.context,
                SharedDocumentInfo,
                ResourcePath("OneDriveSharedItems", self.resource_path),
            ),
        )

    @odata(name="SiteUsers")
    @property
    def site_users(self) -> UserCollection:
        """Specifies the collection of users in the site collection that contains the site"""
        return self.properties.get(
            "SiteUsers",
            UserCollection(self.context, ResourcePath("siteUsers", self.resource_path)),
        )

    @odata(name="SiteGroups")
    @property
    def site_groups(self) -> GroupCollection:
        """Gets the collection of groups for the site collection."""
        return self.properties.get(
            "SiteGroups",
            GroupCollection(self.context, ResourcePath("siteGroups", self.resource_path)),
        )

    @odata(name="CurrentUser")
    @property
    def current_user(self) -> User:
        """Gets the current user."""
        return self.properties.get(
            "CurrentUser",
            User(self.context, ResourcePath("CurrentUser", self.resource_path)),
        )

    @odata(name="ParentWeb")
    @property
    def parent_web(self) -> Web:
        """Gets the parent website of the specified website."""
        return self.properties.get(
            "ParentWeb",
            Web(self.context, ResourcePath("ParentWeb", self.resource_path)),
        )

    @odata(name="AssociatedVisitorGroup")
    @property
    def associated_visitor_group(self) -> Group:
        """Gets or sets the associated visitor group of the Web site."""
        return self.properties.get(
            "AssociatedVisitorGroup",
            Group(self.context, ResourcePath("AssociatedVisitorGroup", self.resource_path)),
        )

    @odata(name="AssociatedOwnerGroup")
    @property
    def associated_owner_group(self) -> Group:
        """Gets or sets the associated owner group of the Web site."""
        return self.properties.get(
            "AssociatedOwnerGroup",
            Group(self.context, ResourcePath("AssociatedOwnerGroup", self.resource_path)),
        )

    @odata(name="AssociatedMemberGroup")
    @property
    def associated_member_group(self) -> Group:
        """Gets or sets the group of users who have been given contribute permissions to the Web site."""
        return self.properties.get(
            "AssociatedMemberGroup",
            Group(self.context, ResourcePath("AssociatedMemberGroup", self.resource_path)),
        )

    @property
    def can_modernize_homepage(self) -> ModernizeHomepageResult:
        """Specifies the site theme associated with the site"""
        return self.properties.get(
            "CanModernizeHomepage",
            ModernizeHomepageResult(self.context, ResourcePath("CanModernizeHomepage", self.resource_path)),
        )

    @property
    def fields(self) -> FieldCollection:
        """Specifies the collection of all the fields (2) in the site (2)."""
        return self.properties.get(
            "Fields",
            FieldCollection(self.context, ResourcePath("Fields", self.resource_path), self),
        )

    @odata(name="ContentTypes")
    @property
    def content_types(self) -> ContentTypeCollection:
        """Gets the collection of content types for the Web site."""
        return self.properties.get(
            "ContentTypes",
            ContentTypeCollection(self.context, ResourcePath("ContentTypes", self.resource_path), self),
        )

    @property
    def configuration(self):
        """
        Specifies the identifier (ID) of the site definition that was used to create the site (2). If the site (2)
        was created with a custom site template this specifies the identifier (ID) of the site definition from which
        the custom site template is derived.
        """
        return self.properties.get("Configuration", None)

    @odata(name="DataLeakagePreventionStatusInfo")
    @property
    def data_leakage_prevention_status_info(self) -> SPDataLeakagePreventionStatusInfo:
        return self.properties.get(
            "DataLeakagePreventionStatusInfo",
            SPDataLeakagePreventionStatusInfo(
                self.context,
                ResourcePath("DataLeakagePreventionStatusInfo", self.resource_path),
            ),
        )

    @odata(name="DescriptionResource")
    @property
    def description_resource(self) -> UserResource:
        """A UserResource object that represents the description of this web."""
        return self.properties.get(
            "DescriptionResource",
            UserResource(self.context, ResourcePath("DescriptionResource", self.resource_path)),
        )

    @odata(name="RoleDefinitions")
    @property
    def role_definitions(self) -> RoleDefinitionCollection:
        """Gets the collection of role definitions for the Web site."""
        return self.properties.get(
            "RoleDefinitions",
            RoleDefinitionCollection(self.context, ResourcePath("RoleDefinitions", self.resource_path)),
        )

    @odata(name="EventReceivers")
    @property
    def event_receivers(self) -> EventReceiverDefinitionCollection:
        """Specifies the collection of event receiver definitions that are currently available on the Web site"""
        return self.properties.get(
            "EventReceivers",
            EventReceiverDefinitionCollection(self.context, ResourcePath("EventReceivers", self.resource_path), self),
        )

    @odata(name="ClientWebParts")
    @property
    def client_web_parts(self) -> ClientWebPartCollection:
        """
        Gets a collection of the ClientWebParts installed in this SP.Web. It can be used to get metadata of the
        ClientWebParts or render them. It is a read-only collection as ClientWebParts need to be installed in
        an app package."""
        return self.properties.get(
            "ClientWebParts",
            ClientWebPartCollection(self.context, ResourcePath("ClientWebParts", self.resource_path)),
        )

    @property
    def features(self) -> FeatureCollection:
        """Get web features"""
        return self.properties.get(
            "Features",
            FeatureCollection(self.context, ResourcePath("Features", self.resource_path), self),
        )

    @odata(name="TenantAppCatalog")
    @property
    def tenant_app_catalog(self) -> TenantCorporateCatalogAccessor:
        """Returns the tenant app catalog for the given tenant if it exists."""
        return self.properties.get(
            "TenantAppCatalog",
            TenantCorporateCatalogAccessor(self.context, ResourcePath("TenantAppCatalog", self.resource_path)),
        )

    @odata(name="SiteCollectionAppCatalog")
    @property
    def site_collection_app_catalog(self) -> SiteCollectionCorporateCatalogAccessor:
        """Returns the site collection app catalog for the given web if it exists."""
        return self.properties.get(
            "SiteCollectionAppCatalog",
            SiteCollectionCorporateCatalogAccessor(
                self.context,
                ResourcePath("SiteCollectionAppCatalog", self.resource_path),
            ),
        )

    @odata(name="WebInfos")
    @property
    def web_infos(self) -> WebInformationCollection:
        """Specifies the collection of all child sites for the site"""
        return self.properties.get(
            "WebInfos",
            WebInformationCollection(self.context, ResourcePath("WebInfos", self.resource_path)),
        )

    @odata(name="ThemeInfo")
    @property
    def theme_info(self) -> ThemeInfo:
        """Specifies the site theme associated with the site"""
        return self.properties.get(
            "ThemeInfo",
            ThemeInfo(self.context, ResourcePath("ThemeInfo", self.resource_path)),
        )

    @property
    def url(self) -> Optional[str]:
        """Gets the absolute URL for the website."""
        return self.properties.get("Url", None)

    @property
    def quick_launch_enabled(self) -> Optional[bool]:
        """Gets a value that specifies whether the Quick Launch area is enabled on the site."""
        return self.properties.get("QuickLaunchEnabled", None)

    @property
    def mega_menu_enabled(self) -> Optional[bool]:
        """Gets a value that specifies whether the Mega menu is enabled on the site."""
        return self.properties.get("MegaMenuEnabled", None)

    @quick_launch_enabled.setter
    def quick_launch_enabled(self, value: bool) -> None:
        """Sets a value that specifies whether the Quick Launch area is enabled on the site."""
        self.set_property("QuickLaunchEnabled", value)

    @property
    def site_logo_url(self) -> Optional[str]:
        """Gets a value that specifies Site logo url."""
        return self.properties.get("SiteLogoUrl", None)

    @odata(name="ListTemplates")
    @property
    def list_templates(self) -> ListTemplateCollection:
        """Gets a value that specifies the collection of list definitions and list templates available for creating
        lists on the site."""
        return self.properties.get(
            "ListTemplates",
            ListTemplateCollection(self.context, ResourcePath("ListTemplates", self.resource_path)),
        )

    @property
    def is_multilingual(self) -> Optional[bool]:
        """Gets whether Multilingual UI is turned on for this web or not."""
        return self.properties.get("IsMultilingual", None)

    @is_multilingual.setter
    def is_multilingual(self, val: bool) -> None:
        """
        Sets whether Multilingual UI is turned on for this web or not.
        """
        self.set_property("IsMultilingual", val)

    @odata(name="MultilingualSettings")
    @property
    def multilingual_settings(self) -> MultilingualSettings:
        """Gets a value that specifies the collection of list definitions and list templates available for creating
        lists on the site."""
        return self.properties.get(
            "MultilingualSettings",
            MultilingualSettings(self.context, ResourcePath("MultilingualSettings", self.resource_path)),
        )

    @property
    def web_template(self) -> Optional[str]:
        """Gets the name of the site definition or site template that was used to create the site."""
        return self.properties.get("WebTemplate", None)

    @odata(name="RegionalSettings")
    @property
    def regional_settings(self) -> RegionalSettings:
        """Gets the regional settings that are currently implemented on the website."""
        return self.properties.get(
            "RegionalSettings",
            RegionalSettings(self.context, ResourcePath("RegionalSettings", self.resource_path)),
        )

    @odata(name="RecycleBin")
    @property
    def recycle_bin(self) -> RecycleBinItemCollection:
        """Specifies the collection of Recycle Bin items of the Recycle Bin of the site"""
        return self.properties.get(
            "RecycleBin",
            RecycleBinItemCollection(self.context, ResourcePath("RecycleBin", self.resource_path)),
        )

    @property
    def recycle_bin_enabled(self) -> Optional[bool]:
        """Specifies whether the Recycle Bin is enabled."""
        return self.properties.get("RecycleBinEnabled", None)

    @property
    def related_hub_site_ids(self) -> Optional[str]:
        """ """
        return self.properties.get("RelatedHubSiteIds", None)

    @property
    def request_access_email(self) -> Optional[str]:
        """Gets the e-mail address to which requests for access are sent."""
        return self.properties.get("RequestAccessEmail", None)

    @property
    def save_site_as_template_enabled(self) -> Optional[bool]:
        """Specifies if the site (2) can be saved as a site template.

        A feature that creates content which is not compatible for a site template can set this value to false to
        stop users of this site (2) from generating an invalid site template.

        A feature ought to never set this value to true when it is deactivated or at any other time since another
        feature might have created content that is not compatible in a site template.

        Setting this value to false, if it was true, will result in a site template that is not supported.
        """
        return self.properties.get("SaveSiteAsTemplateEnabled", None)

    @property
    def search_box_in_navbar(self) -> Optional[int]:
        """Gets the e-mail address to which requests for access are sent."""
        return self.properties.get("SearchBoxInNavBar", None)

    @property
    def search_box_placeholder_text(self) -> Optional[str]:
        """Gets the placeholder text in SharePoint online search box for a given (sub) site."""
        return self.properties.get("SearchBoxPlaceholderText", None)

    @property
    def navigation(self) -> Navigation:
        """Specifies the navigation structure on the site (2), including the Quick Launch area and the link bar."""
        return self.properties.get(
            "Navigation",
            Navigation(self.context, ResourcePath("Navigation", self.resource_path)),
        )

    @odata(name="PushNotificationSubscribers")
    @property
    def push_notification_subscribers(self) -> PushNotificationSubscriberCollection:
        """Specifies the collection of push notification subscribers for the site"""
        return self.properties.get(
            "PushNotificationSubscribers",
            PushNotificationSubscriberCollection(
                self.context,
                ResourcePath("PushNotificationSubscribers", self.resource_path),
            ),
        )

    @odata(name="RootFolder")
    @property
    def root_folder(self) -> Folder:
        """Get a root folder"""
        return self.properties.get(
            "RootFolder",
            Folder(self.context, ResourcePath("RootFolder", self.resource_path)),
        )

    @property
    def alerts(self) -> AlertCollection:
        """Gets the collection of alerts for the site or subsite."""
        return self.properties.get(
            "Alerts",
            AlertCollection(self.context, ResourcePath("Alerts", self.resource_path)),
        )

    @odata(name="AvailableFields")
    @property
    def available_fields(self) -> FieldCollection:
        """
        Specifies the collection of all fields available for the current scope, including those of the
        current site, as well as any parent sites.
        """
        return self.properties.get(
            "AvailableFields",
            FieldCollection(self.context, ResourcePath("AvailableFields", self.resource_path)),
        )

    @odata(name="AvailableContentTypes")
    @property
    def available_content_types(self) -> ContentTypeCollection:
        """
        Specifies the collection of all site content types that apply to the current scope,
        including those of the current site (2), as well as any parent sites.
        """
        return self.properties.get(
            "AvailableContentTypes",
            ContentTypeCollection(self.context, ResourcePath("AvailableContentTypes", self.resource_path)),
        )

    @odata(name="SiteUserInfoList")
    @property
    def site_user_info_list(self) -> List:
        """
        Specifies the user information list for the site collection that contains the site
        """
        return self.properties.get(
            "SiteUserInfoList",
            List(self.context, ResourcePath("SiteUserInfoList", self.resource_path)),
        )

    @property
    def title(self) -> Optional[str]:
        """Gets the title of the web."""
        return self.properties.get("Title", None)

    @property
    def welcome_page(self) -> Optional[str]:
        """Specifies the URL of the Welcome page for the site"""
        return self.properties.get("WelcomePage", None)

    @odata(name="SupportedUILanguageIds")
    @property
    def supported_ui_language_ids(self) -> ClientValueCollection[int]:
        """Specifies the language code identifiers (LCIDs) of the languages that are enabled for the site."""
        return self.properties.get("SupportedUILanguageIds", ClientValueCollection(int))

    @property
    def ui_version(self) -> Optional[int]:
        """Gets or sets the user interface (UI) version of the Web site."""
        return self.properties.get("UIVersion", None)

    @odata(name="UserCustomActions")
    @property
    def user_custom_actions(self) -> UserCustomActionCollection:
        """Specifies the collection of user custom actions for the site"""
        return self.properties.get(
            "UserCustomActions",
            UserCustomActionCollection(self.context, ResourcePath("UserCustomActions", self.resource_path)),
        )

    @property
    def server_relative_path(self) -> SPResPath:
        """Gets the server-relative Path of the Web."""
        return self.properties.get("ServerRelativePath", SPResPath())

    @property
    def syndication_enabled(self) -> Optional[bool]:
        """Specifies whether the [RSS2.0] feeds are enabled on the site"""
        return self.properties.get("SyndicationEnabled", None)

    @odata(name="TitleResource")
    @property
    def title_resource(self) -> UserResource:
        """A UserResource object that represents the title of this web."""
        return self.properties.get(
            "TitleResource",
            UserResource(self.context, ResourcePath("TitleResource", self.resource_path)),
        )

    @odata(name="AllProperties")
    @property
    def all_properties(self) -> PropertyValues:
        """A UserResource object that represents the title of this web."""
        return self.properties.get(
            "AllProperties",
            PropertyValues(self.context, ResourcePath("AllProperties", self.resource_path)),
        )

    @property
    def treeview_enabled(self) -> Optional[bool]:
        """Specifies whether the tree view is enabled on the site"""
        return self.properties.get("TreeViewEnabled", None)

    @property
    def taxonomy_list(self) -> List:
        """A special list that stores the mapping between taxonomy term IDs and their corresponding values"""
        return self.lists.get_by_title("TaxonomyHiddenList")

    def set_property(self, name, value, persist_changes=True):
        super().set_property(name, value, persist_changes)
        if name == "Url":
            self._web_url = value
            assert self._resource_path is not None
            self._resource_path.set_segment(value)
        return self

    @property
    def resource_url(self) -> str:
        """Returns Web url"""
        orig_resource_url = super().resource_url or ""
        if self._web_url is not None:
            orig_resource_url = orig_resource_url.replace(self.context.service_root_url, self._web_url + "/_api")
        return orig_resource_url

    @property
    def access_request_site_description(self) -> Optional[str]:
        """Gets the AccessRequestSiteDescription property"""
        return self.properties.get("AccessRequestSiteDescription", None)

    @property
    def acronym(self) -> Optional[str]:
        """Gets the Acronym property"""
        return self.properties.get("Acronym", None)

    @property
    def allow_automatic_aspx_page_indexing(self) -> Optional[bool]:
        """Gets the AllowAutomaticASPXPageIndexing property"""
        return self.properties.get("AllowAutomaticASPXPageIndexing", None)

    @property
    def allow_create_declarative_workflow_for_current_user(self) -> Optional[bool]:
        """Gets the AllowCreateDeclarativeWorkflowForCurrentUser property"""
        return self.properties.get("AllowCreateDeclarativeWorkflowForCurrentUser", None)

    @property
    def allow_save_declarative_workflow_as_template_for_current_user(self) -> Optional[bool]:
        """Gets the AllowSaveDeclarativeWorkflowAsTemplateForCurrentUser property"""
        return self.properties.get("AllowSaveDeclarativeWorkflowAsTemplateForCurrentUser", None)

    @property
    def allow_save_publish_declarative_workflow_for_current_user(self) -> Optional[bool]:
        """Gets the AllowSavePublishDeclarativeWorkflowForCurrentUser property"""
        return self.properties.get("AllowSavePublishDeclarativeWorkflowForCurrentUser", None)

    @property
    def classic_welcome_page(self) -> Optional[str]:
        """Gets the ClassicWelcomePage property"""
        return self.properties.get("ClassicWelcomePage", None)

    @property
    def comments_on_site_pages_disabled(self) -> Optional[bool]:
        """Gets the CommentsOnSitePagesDisabled property"""
        return self.properties.get("CommentsOnSitePagesDisabled", None)

    @property
    def contains_confidential_info(self) -> Optional[bool]:
        """Gets the ContainsConfidentialInfo property"""
        return self.properties.get("ContainsConfidentialInfo", None)

    @property
    def current_change_token(self) -> ChangeToken:
        """Gets the CurrentChangeToken property"""
        from office365.sharepoint.changes.token import ChangeToken

        return self.properties.get("CurrentChangeToken", ChangeToken())

    @property
    def default_new_page_template_id(self) -> Optional[UUID]:
        """Gets the DefaultNewPageTemplateId property"""
        return self.properties.get("DefaultNewPageTemplateId", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)

    @property
    def description_for_existing_language(self) -> Optional[str]:
        """Gets the DescriptionForExistingLanguage property"""
        return self.properties.get("DescriptionForExistingLanguage", None)

    @property
    def designer_download_url_for_current_user(self) -> Optional[str]:
        """Gets the DesignerDownloadUrlForCurrentUser property"""
        return self.properties.get("DesignerDownloadUrlForCurrentUser", None)

    @property
    def disable_recommended_items(self) -> Optional[bool]:
        """Gets the DisableRecommendedItems property"""
        return self.properties.get("DisableRecommendedItems", None)

    @property
    def document_library_callout_office_web_app_previewers_disabled(self) -> Optional[bool]:
        """Gets the DocumentLibraryCalloutOfficeWebAppPreviewersDisabled property"""
        return self.properties.get("DocumentLibraryCalloutOfficeWebAppPreviewersDisabled", None)

    @property
    def exclude_from_offline_client(self) -> Optional[bool]:
        """Gets the ExcludeFromOfflineClient property"""
        return self.properties.get("ExcludeFromOfflineClient", None)

    @property
    def font_option_for_site_footer_nav(self) -> FontOption:
        """Gets the FontOptionForSiteFooterNav property"""
        from office365.sharepoint.documents.fontoption import FontOption

        return self.properties.get("FontOptionForSiteFooterNav", FontOption())

    @property
    def font_option_for_site_footer_title(self) -> FontOption:
        """Gets the FontOptionForSiteFooterTitle property"""
        from office365.sharepoint.documents.fontoption import FontOption

        return self.properties.get("FontOptionForSiteFooterTitle", FontOption())

    @property
    def font_option_for_site_nav(self) -> FontOption:
        """Gets the FontOptionForSiteNav property"""
        from office365.sharepoint.documents.fontoption import FontOption

        return self.properties.get("FontOptionForSiteNav", FontOption())

    @property
    def font_option_for_site_title(self) -> FontOption:
        """Gets the FontOptionForSiteTitle property"""
        from office365.sharepoint.documents.fontoption import FontOption

        return self.properties.get("FontOptionForSiteTitle", FontOption())

    @property
    def footer_alignment(self) -> Optional[int]:
        """Gets the FooterAlignment property"""
        return self.properties.get("FooterAlignment", None)

    @property
    def footer_background_focal_point(self) -> SPFocalPoint:
        """Gets the FooterBackgroundFocalPoint property"""
        from office365.sharepoint.webs.sp_focal_point import SPFocalPoint

        return self.properties.get("FooterBackgroundFocalPoint", SPFocalPoint())

    @property
    def footer_blur(self) -> Optional[int]:
        """Gets the FooterBlur property"""
        return self.properties.get("FooterBlur", None)

    @property
    def footer_color_index_in_dark_mode(self) -> Optional[int]:
        """Gets the FooterColorIndexInDarkMode property"""
        return self.properties.get("FooterColorIndexInDarkMode", None)

    @property
    def footer_color_index_in_light_mode(self) -> Optional[int]:
        """Gets the FooterColorIndexInLightMode property"""
        return self.properties.get("FooterColorIndexInLightMode", None)

    @property
    def footer_emphasis(self) -> Optional[int]:
        """Gets the FooterEmphasis property"""
        return self.properties.get("FooterEmphasis", None)

    @property
    def footer_enabled(self) -> Optional[bool]:
        """Gets the FooterEnabled property"""
        return self.properties.get("FooterEnabled", None)

    @property
    def footer_layout(self) -> Optional[int]:
        """Gets the FooterLayout property"""
        return self.properties.get("FooterLayout", None)

    @property
    def footer_overlay_color(self) -> Optional[int]:
        """Gets the FooterOverlayColor property"""
        return self.properties.get("FooterOverlayColor", None)

    @property
    def footer_overlay_gradient_direction(self) -> Optional[int]:
        """Gets the FooterOverlayGradientDirection property"""
        return self.properties.get("FooterOverlayGradientDirection", None)

    @property
    def footer_overlay_opacity(self) -> Optional[int]:
        """Gets the FooterOverlayOpacity property"""
        return self.properties.get("FooterOverlayOpacity", None)

    @property
    def has_footer_background_image(self) -> Optional[bool]:
        """Gets the HasFooterBackgroundImage property"""
        return self.properties.get("HasFooterBackgroundImage", None)

    @property
    def has_header_background_image(self) -> Optional[bool]:
        """Gets the HasHeaderBackgroundImage property"""
        return self.properties.get("HasHeaderBackgroundImage", None)

    @property
    def has_web_template_extension(self) -> Optional[bool]:
        """Gets the HasWebTemplateExtension property"""
        return self.properties.get("HasWebTemplateExtension", None)

    @property
    def header_color_index_in_dark_mode(self) -> Optional[int]:
        """Gets the HeaderColorIndexInDarkMode property"""
        return self.properties.get("HeaderColorIndexInDarkMode", None)

    @property
    def header_color_index_in_light_mode(self) -> Optional[int]:
        """Gets the HeaderColorIndexInLightMode property"""
        return self.properties.get("HeaderColorIndexInLightMode", None)

    @property
    def header_emphasis(self) -> Optional[int]:
        """Gets the HeaderEmphasis property"""
        return self.properties.get("HeaderEmphasis", None)

    @property
    def header_layout(self) -> Optional[int]:
        """Gets the HeaderLayout property"""
        return self.properties.get("HeaderLayout", None)

    @property
    def header_overlay_color(self) -> Optional[int]:
        """Gets the HeaderOverlayColor property"""
        return self.properties.get("HeaderOverlayColor", None)

    @property
    def header_overlay_gradient_direction(self) -> Optional[int]:
        """Gets the HeaderOverlayGradientDirection property"""
        return self.properties.get("HeaderOverlayGradientDirection", None)

    @property
    def header_overlay_opacity(self) -> Optional[int]:
        """Gets the HeaderOverlayOpacity property"""
        return self.properties.get("HeaderOverlayOpacity", None)

    @property
    def hide_title_in_header(self) -> Optional[bool]:
        """Gets the HideTitleInHeader property"""
        return self.properties.get("HideTitleInHeader", None)

    @property
    def horizontal_quick_launch(self) -> Optional[bool]:
        """Gets the HorizontalQuickLaunch property"""
        return self.properties.get("HorizontalQuickLaunch", None)

    @property
    def is_edu_class(self) -> Optional[bool]:
        """Gets the IsEduClass property"""
        return self.properties.get("IsEduClass", None)

    @property
    def is_edu_class_provision_checked(self) -> Optional[bool]:
        """Gets the IsEduClassProvisionChecked property"""
        return self.properties.get("IsEduClassProvisionChecked", None)

    @property
    def is_edu_class_provision_pending(self) -> Optional[bool]:
        """Gets the IsEduClassProvisionPending property"""
        return self.properties.get("IsEduClassProvisionPending", None)

    @property
    def is_homepage_modernized(self) -> Optional[bool]:
        """Gets the IsHomepageModernized property"""
        return self.properties.get("IsHomepageModernized", None)

    @property
    def is_provisioning_complete(self) -> Optional[bool]:
        """Gets the IsProvisioningComplete property"""
        return self.properties.get("IsProvisioningComplete", None)

    @property
    def is_revert_homepage_link_hidden(self) -> Optional[bool]:
        """Gets the IsRevertHomepageLinkHidden property"""
        return self.properties.get("IsRevertHomepageLinkHidden", None)

    @property
    def last_item_user_modified_date(self) -> Optional[datetime]:
        """Gets the LastItemUserModifiedDate property"""
        return self.properties.get("LastItemUserModifiedDate", datetime.min)

    @property
    def logo_alignment(self) -> Optional[int]:
        """Gets the LogoAlignment property"""
        return self.properties.get("LogoAlignment", None)

    @property
    def master_url(self) -> Optional[str]:
        """Gets the MasterUrl property"""
        return self.properties.get("MasterUrl", None)

    @property
    def members_can_share(self) -> Optional[bool]:
        """Gets the MembersCanShare property"""
        return self.properties.get("MembersCanShare", None)

    @property
    def nav_audience_targeting_enabled(self) -> Optional[bool]:
        """Gets the NavAudienceTargetingEnabled property"""
        return self.properties.get("NavAudienceTargetingEnabled", None)

    @property
    def next_steps_first_run_enabled(self) -> Optional[bool]:
        """Gets the NextStepsFirstRunEnabled property"""
        return self.properties.get("NextStepsFirstRunEnabled", None)

    @property
    def no_crawl(self) -> Optional[bool]:
        """Gets the NoCrawl property"""
        return self.properties.get("NoCrawl", None)

    @property
    def notifications_in_onedrive_for_business_enabled(self) -> Optional[bool]:
        """Gets the NotificationsInOneDriveForBusinessEnabled property"""
        return self.properties.get("NotificationsInOneDriveForBusinessEnabled", None)

    @property
    def notifications_in_sharepoint_enabled(self) -> Optional[bool]:
        """Gets the NotificationsInSharePointEnabled property"""
        return self.properties.get("NotificationsInSharePointEnabled", None)

    @property
    def object_cache_enabled(self) -> Optional[bool]:
        """Gets the ObjectCacheEnabled property"""
        return self.properties.get("ObjectCacheEnabled", None)

    @property
    def overwrite_translations_on_change(self) -> Optional[bool]:
        """Gets the OverwriteTranslationsOnChange property"""
        return self.properties.get("OverwriteTranslationsOnChange", None)

    @property
    def preview_features_enabled(self) -> Optional[bool]:
        """Gets the PreviewFeaturesEnabled property"""
        return self.properties.get("PreviewFeaturesEnabled", None)

    @property
    def primary_color(self) -> Optional[str]:
        """Gets the PrimaryColor property"""
        return self.properties.get("PrimaryColor", None)

    @property
    def search_box_in_nav_bar(self) -> Optional[int]:
        """Gets the SearchBoxInNavBar property"""
        return self.properties.get("SearchBoxInNavBar", None)

    @property
    def search_scope(self) -> Optional[int]:
        """Gets the SearchScope property"""
        return self.properties.get("SearchScope", None)

    @property
    def server_relative_url(self) -> Optional[str]:
        """Gets the ServerRelativeUrl property"""
        return self.properties.get("ServerRelativeUrl", None)

    @property
    def should_extend_header_bg_image_to_nav(self) -> Optional[str]:
        """Gets the ShouldExtendHeaderBgImageToNav property"""
        return self.properties.get("ShouldExtendHeaderBgImageToNav", None)

    @property
    def show_url_structure_for_current_user(self) -> Optional[bool]:
        """Gets the ShowUrlStructureForCurrentUser property"""
        return self.properties.get("ShowUrlStructureForCurrentUser", None)

    @property
    def site_logo_description(self) -> Optional[str]:
        """Gets the SiteLogoDescription property"""
        return self.properties.get("SiteLogoDescription", None)

    @property
    def tenant_admin_members_can_share(self) -> Optional[int]:
        """Gets the TenantAdminMembersCanShare property"""
        return self.properties.get("TenantAdminMembersCanShare", None)

    @property
    def tenant_tag_policy_enabled(self) -> Optional[bool]:
        """Gets the TenantTagPolicyEnabled property"""
        return self.properties.get("TenantTagPolicyEnabled", None)

    @property
    def theme_application_action_history(self) -> Optional[str]:
        """Gets the ThemeApplicationActionHistory property"""
        return self.properties.get("ThemeApplicationActionHistory", None)

    @property
    def theme_data(self) -> Optional[str]:
        """Gets the ThemeData property"""
        return self.properties.get("ThemeData", None)

    @property
    def themed_css_folder_url(self) -> Optional[str]:
        """Gets the ThemedCssFolderUrl property"""
        return self.properties.get("ThemedCssFolderUrl", None)

    @property
    def third_party_mdm_enabled(self) -> Optional[bool]:
        """Gets the ThirdPartyMdmEnabled property"""
        return self.properties.get("ThirdPartyMdmEnabled", None)

    @property
    def title_for_existing_language(self) -> Optional[str]:
        """Gets the TitleForExistingLanguage property"""
        return self.properties.get("TitleForExistingLanguage", None)

    @property
    def title_translations(self) -> ClientValueCollection[SPResourceEntry]:
        """Gets the TitleTranslations property"""
        from office365.sharepoint.translation.resource_entry import SPResourceEntry

        return self.properties.get("TitleTranslations", ClientValueCollection[SPResourceEntry](SPResourceEntry))

    @property
    def tree_view_enabled(self) -> Optional[bool]:
        """Gets the TreeViewEnabled property"""
        return self.properties.get("TreeViewEnabled", None)

    @property
    def ui_version_configuration_enabled(self) -> Optional[bool]:
        """Gets the UIVersionConfigurationEnabled property"""
        return self.properties.get("UIVersionConfigurationEnabled", None)

    @property
    def use_access_request_default(self) -> Optional[bool]:
        """Gets the UseAccessRequestDefault property"""
        return self.properties.get("UseAccessRequestDefault", None)

    @property
    def web_template_configuration(self) -> Optional[str]:
        """Gets the WebTemplateConfiguration property"""
        return self.properties.get("WebTemplateConfiguration", None)

    @property
    def web_templates_gallery_first_run_enabled(self) -> Optional[bool]:
        """Gets the WebTemplatesGalleryFirstRunEnabled property"""
        return self.properties.get("WebTemplatesGalleryFirstRunEnabled", None)

    @property
    def app_tiles(self) -> EntityCollection[AppTile]:
        """Gets the AppTiles property"""
        from office365.sharepoint.webs.apptile import AppTile

        return self.properties.get(
            "AppTiles", EntityCollection[AppTile](self.context, AppTile, ResourcePath("AppTiles", self.resource_path))
        )

    @property
    def card_designs(self) -> CardDesigns:
        """Gets the CardDesigns property"""
        from office365.sharepoint.marketplace.corporatecuratedgallery.carddesigns.card_designs import (
            CardDesigns,
        )

        return self.properties.get(
            "CardDesigns", CardDesigns(self.context, ResourcePath("CardDesigns", self.resource_path))
        )

    @property
    def folder_coloring(self) -> FolderColoring:
        """Gets the FolderColoring property"""
        from office365.sharepoint.folders.coloring import FolderColoring

        return self.properties.get(
            "FolderColoring", FolderColoring(self.context, ResourcePath("FolderColoring", self.resource_path))
        )

    @property
    def workflow_associations(self) -> EntityCollection[WorkflowAssociation]:
        """Gets the WorkflowAssociations property"""
        from office365.sharepoint.workflow.associations.association import (
            WorkflowAssociation,
        )

        return self.properties.get(
            "WorkflowAssociations",
            EntityCollection[WorkflowAssociation](
                self.context, WorkflowAssociation, ResourcePath("WorkflowAssociations", self.resource_path)
            ),
        )

    @property
    def workflow_templates(self) -> EntityCollection[WorkflowTemplate]:
        """Gets the WorkflowTemplates property"""
        from office365.sharepoint.workflow.template import WorkflowTemplate

        return self.properties.get(
            "WorkflowTemplates",
            EntityCollection[WorkflowTemplate](
                self.context, WorkflowTemplate, ResourcePath("WorkflowTemplates", self.resource_path)
            ),
        )

    def addin_permissions(
        self, addins: ClientValueCollection[SPAddinPermissionRequest]
    ) -> ClientResult[SPAddinPermissionResponse]:
        """AddinPermissions operation.

        Args:
            addins (ClientValueCollection[SPAddinPermissionRequest]):
                addins parameter
        """
        from office365.sharepoint.marketplace.corporatecuratedgallery.addins.permission_response import (
            SPAddinPermissionResponse,
        )

        return_type = ClientResult(self.context, SPAddinPermissionResponse())
        qry = ServiceOperationQuery(self, "AddinPermissions", None, {"addins": addins}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_placeholder_user(self, list_id: str, placeholder_text: str) -> ClientResult[UUID]:
        """AddPlaceholderUser operation.

        Args:
            list_id (str):
                listId parameter
            placeholder_text (str):
                placeholderText parameter
        """
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(
            self, "AddPlaceholderUser", None, {"listId": list_id, "placeholderText": placeholder_text}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def apply_theme(
        self, color_palette_url: str, font_scheme_url: str, background_image_url: str, share_generated: bool
    ) -> Self:
        """ApplyTheme operation.

        Args:
            color_palette_url (str):
                colorPaletteUrl parameter
            font_scheme_url (str):
                fontSchemeUrl parameter
            background_image_url (str):
                backgroundImageUrl parameter
            share_generated (bool):
                shareGenerated parameter
        """
        qry = ServiceOperationQuery(
            self,
            "ApplyTheme",
            None,
            {
                "colorPaletteUrl": color_palette_url,
                "fontSchemeUrl": font_scheme_url,
                "backgroundImageUrl": background_image_url,
                "shareGenerated": share_generated,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def content_by_query_replay(
        self, webs: str, lists: str, caml_query: str, view_fields: str, row_limit: int
    ) -> ClientResult[str]:
        """ContentByQueryReplay operation.

        Args:
            webs (str):
                webs parameter
            lists (str):
                lists parameter
            caml_query (str):
                camlQuery parameter
            view_fields (str):
                viewFields parameter
            row_limit (int):
                rowLimit parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "ContentByQueryReplay", [webs, lists, caml_query, view_fields, row_limit], return_type)
        self.context.add_query(qry)
        return return_type

    def convert_html_to_email_safe_html(
        self, html_body: str, remove_embedded_images: bool, feedback_source_url: str
    ) -> ClientResult[str]:
        """ConvertHtmlToEmailSafeHtml operation.

        Args:
            html_body (str):
                htmlBody parameter
            remove_embedded_images (bool):
                removeEmbeddedImages parameter
            feedback_source_url (str):
                feedbackSourceUrl parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "ConvertHtmlToEmailSafeHtml",
            None,
            {
                "htmlBody": html_body,
                "removeEmbeddedImages": remove_embedded_images,
                "feedbackSourceUrl": feedback_source_url,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def execute_remote_lob(self, input_stream: bytes) -> ClientResult[bytes]:
        """ExecuteRemoteLOB operation.

        Args:
            input_stream (bytes):
                inputStream parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(self, "ExecuteRemoteLOB", None, {"inputStream": input_stream}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_addin_uninstall_job_detail(
        self, job_id: UUID, server_relative_url: str, url: str
    ) -> ClientResult[SPUninstallAddinJobDetail]:
        """GetAddinUninstallJobDetail operation.

        Args:
            job_id (UUID):
                jobId parameter
            server_relative_url (str):
                serverRelativeUrl parameter
            url (str):
                url parameter
        """
        from office365.sharepoint.marketplace.corporatecuratedgallery.spuninstalladdinjobdetail import (
            SPUninstallAddinJobDetail,
        )

        return_type = ClientResult(self.context, SPUninstallAddinJobDetail())
        qry = ServiceOperationQuery(
            self,
            "GetAddinUninstallJobDetail",
            None,
            {"jobId": job_id, "serverRelativeUrl": server_relative_url, "url": url},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_sp_app_context_as_stream(self) -> ClientResult[bytes]:
        """GetSPAppContextAsStream operation."""
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "GetSPAppContextAsStream", [], return_type, return_raw_content=True)
        self.context.add_query(qry)
        return return_type

    def hub_site_data_as_stream(self, force_refresh: bool) -> ClientResult[bytes]:
        """HubSiteDataAsStream operation.

        Args:
            force_refresh (bool):
                forceRefresh parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "HubSiteDataAsStream", [force_refresh], return_type, return_raw_content=True)
        self.context.add_query(qry)
        return return_type

    def map_to_icon(self, file_name: str, prog_id: str, size: int) -> ClientResult[str]:
        """MapToIcon operation.

        Args:
            file_name (str):
                fileName parameter
            prog_id (str):
                progId parameter
            size (int):
                size parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "MapToIcon", [file_name, prog_id, size], return_type)
        self.context.add_query(qry)
        return return_type

    def mark_reply_uris_updated(self) -> Self:
        """MarkReplyUrisUpdated operation."""
        qry = ServiceOperationQuery(self, "MarkReplyUrisUpdated", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def page_context_core(self) -> ClientResult[bytes]:
        """PageContextCore operation."""
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "PageContextCore", [], return_type, return_raw_content=True)
        self.context.add_query(qry)
        return return_type

    def process_external_notification(self, stream: bytes) -> ClientResult[str]:
        """ProcessExternalNotification operation.

        Args:
            stream (bytes):
                stream parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "ProcessExternalNotification", None, {"stream": stream}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def recycle(self) -> Self:
        """Recycle operation."""
        qry = ServiceOperationQuery(self, "Recycle", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def send_notification_tool(
        self,
        recipients: list[str],
        cc_recipients: list[str],
        bcc_recipients: list[str],
        html_body: str,
        subject: str,
        skip_html_conversion: bool,
        feedback_source_url: str,
    ) -> ClientResult[str]:
        """SendNotificationTool operation.

        Args:
            recipients (list[str]):
                recipients parameter
            cc_recipients (list[str]):
                ccRecipients parameter
            bcc_recipients (list[str]):
                bccRecipients parameter
            html_body (str):
                htmlBody parameter
            subject (str):
                subject parameter
            skip_html_conversion (bool):
                skipHtmlConversion parameter
            feedback_source_url (str):
                feedbackSourceUrl parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "SendNotificationTool",
            None,
            {
                "recipients": StringCollection(recipients),
                "ccRecipients": StringCollection(cc_recipients),
                "bccRecipients": StringCollection(bcc_recipients),
                "htmlBody": html_body,
                "subject": subject,
                "skipHtmlConversion": skip_html_conversion,
                "feedbackSourceUrl": feedback_source_url,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_chrome_options(
        self,
        header_layout: int,
        header_emphasis: int,
        mega_menu_enabled: bool,
        footer_enabled: bool,
        footer_layout: int,
        footer_emphasis: int,
        hide_title_in_header: bool,
        logo_alignment: int,
        horizontal_quick_launch: bool,
        header_color_index_in_light_mode: int,
        header_color_index_in_dark_mode: int,
        footer_color_index_in_light_mode: int,
        footer_color_index_in_dark_mode: int,
        footer_alignment: int,
        footer_blur: int,
        header_overlay_color: int,
        header_overlay_gradient_direction: int,
        header_overlay_opacity: int,
        footer_overlay_color: int,
        footer_overlay_gradient_direction: int,
        footer_overlay_opacity: int,
        font_option_for_site_title: FontOption,
        font_option_for_site_nav: FontOption,
        font_option_for_site_footer_title: FontOption,
        font_option_for_site_footer_nav: FontOption,
        should_extend_header_bg_image_to_nav: str,
    ) -> ClientResult[str]:
        """SetChromeOptions operation.

        Args:
            header_layout (int):
                headerLayout parameter
            header_emphasis (int):
                headerEmphasis parameter
            mega_menu_enabled (bool):
                megaMenuEnabled parameter
            footer_enabled (bool):
                footerEnabled parameter
            footer_layout (int):
                footerLayout parameter
            footer_emphasis (int):
                footerEmphasis parameter
            hide_title_in_header (bool):
                hideTitleInHeader parameter
            logo_alignment (int):
                logoAlignment parameter
            horizontal_quick_launch (bool):
                horizontalQuickLaunch parameter
            header_color_index_in_light_mode (int):
                headerColorIndexInLightMode parameter
            header_color_index_in_dark_mode (int):
                headerColorIndexInDarkMode parameter
            footer_color_index_in_light_mode (int):
                footerColorIndexInLightMode parameter
            footer_color_index_in_dark_mode (int):
                footerColorIndexInDarkMode parameter
            footer_alignment (int):
                footerAlignment parameter
            footer_blur (int):
                footerBlur parameter
            header_overlay_color (int):
                headerOverlayColor parameter
            header_overlay_gradient_direction (int):
                headerOverlayGradientDirection parameter
            header_overlay_opacity (int):
                headerOverlayOpacity parameter
            footer_overlay_color (int):
                footerOverlayColor parameter
            footer_overlay_gradient_direction (int):
                footerOverlayGradientDirection parameter
            footer_overlay_opacity (int):
                footerOverlayOpacity parameter
            font_option_for_site_title (FontOption):
                fontOptionForSiteTitle parameter
            font_option_for_site_nav (FontOption):
                fontOptionForSiteNav parameter
            font_option_for_site_footer_title (FontOption):
                fontOptionForSiteFooterTitle parameter
            font_option_for_site_footer_nav (FontOption):
                fontOptionForSiteFooterNav parameter
            should_extend_header_bg_image_to_nav (str):
                shouldExtendHeaderBgImageToNav parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "SetChromeOptions",
            None,
            {
                "headerLayout": header_layout,
                "headerEmphasis": header_emphasis,
                "megaMenuEnabled": mega_menu_enabled,
                "footerEnabled": footer_enabled,
                "footerLayout": footer_layout,
                "footerEmphasis": footer_emphasis,
                "hideTitleInHeader": hide_title_in_header,
                "logoAlignment": logo_alignment,
                "horizontalQuickLaunch": horizontal_quick_launch,
                "headerColorIndexInLightMode": header_color_index_in_light_mode,
                "headerColorIndexInDarkMode": header_color_index_in_dark_mode,
                "footerColorIndexInLightMode": footer_color_index_in_light_mode,
                "footerColorIndexInDarkMode": footer_color_index_in_dark_mode,
                "footerAlignment": footer_alignment,
                "footerBlur": footer_blur,
                "headerOverlayColor": header_overlay_color,
                "headerOverlayGradientDirection": header_overlay_gradient_direction,
                "headerOverlayOpacity": header_overlay_opacity,
                "footerOverlayColor": footer_overlay_color,
                "footerOverlayGradientDirection": footer_overlay_gradient_direction,
                "footerOverlayOpacity": footer_overlay_opacity,
                "fontOptionForSiteTitle": font_option_for_site_title,
                "fontOptionForSiteNav": font_option_for_site_nav,
                "fontOptionForSiteFooterTitle": font_option_for_site_footer_title,
                "fontOptionForSiteFooterNav": font_option_for_site_footer_nav,
                "shouldExtendHeaderBgImageToNav": should_extend_header_bg_image_to_nav,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_default_new_page_template_id(self, default_new_page_template_id: UUID) -> Self:
        """SetDefaultNewPageTemplateId operation.

        Args:
            default_new_page_template_id (UUID):
                defaultNewPageTemplateId parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetDefaultNewPageTemplateId",
            None,
            {"defaultNewPageTemplateId": default_new_page_template_id},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_theme_application_action_history(self, theme_application_action_history: str) -> Self:
        """SetThemeApplicationActionHistory operation.

        Args:
            theme_application_action_history (str):
                themeApplicationActionHistory parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetThemeApplicationActionHistory",
            None,
            {"themeApplicationActionHistory": theme_application_action_history},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_use_access_request_default_and_update(self, use_access_request_default: bool) -> Self:
        """SetUseAccessRequestDefaultAndUpdate operation.

        Args:
            use_access_request_default (bool):
                useAccessRequestDefault parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetUseAccessRequestDefaultAndUpdate",
            None,
            {"useAccessRequestDefault": use_access_request_default},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def sync_teams_component(
        self, teams_component: SPTeamsAppComponent
    ) -> ClientResult[SPClientSideComponentQueryResult]:
        """SyncTeamsComponent operation.

        Args:
            teams_component (SPTeamsAppComponent):
                teamsComponent parameter
        """
        from office365.sharepoint.clientsidecomponent.query_result import (
            SPClientSideComponentQueryResult,
        )

        return_type = ClientResult(self.context, SPClientSideComponentQueryResult())
        qry = ServiceOperationQuery(
            self, "SyncTeamsComponent", None, {"teamsComponent": teams_component}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def uninstall_addins(
        self, uninstall_addins: ClientValueCollection[SPUninstallAddinRequest]
    ) -> ClientResult[SPUninstallAddinResponse]:
        """UninstallAddins operation.

        Args:
            uninstall_addins (ClientValueCollection[SPUninstallAddinRequest]):
                uninstallAddins parameter
        """
        from office365.sharepoint.marketplace.corporatecuratedgallery.spuninstalladdinresponse import (
            SPUninstallAddinResponse,
        )

        return_type = ClientResult(self.context, SPUninstallAddinResponse())
        qry = ServiceOperationQuery(
            self, "UninstallAddins", None, {"uninstallAddins": uninstall_addins}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def unset_is_edu_class_provision_pending(self) -> Self:
        """UnsetIsEduClassProvisionPending operation."""
        qry = ServiceOperationQuery(self, "UnsetIsEduClassProvisionPending", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def upgrade_prefab_app_instance(
        self, prefab_item_id: int, has_custom_upgrade_configuration: bool
    ) -> ClientResult[bool]:
        """UpgradePrefabAppInstance operation.

        Args:
            prefab_item_id (int):
                prefabItemId parameter
            has_custom_upgrade_configuration (bool):
                hasCustomUpgradeConfiguration parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self,
            "UpgradePrefabAppInstance",
            None,
            {"prefabItemId": prefab_item_id, "hasCustomUpgradeConfiguration": has_custom_upgrade_configuration},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def upload_image(
        self,
        list_title: str,
        image_name: str,
        content_stream: bytes,
        list_id: str,
        item_id: int,
        field_id: str,
        overwrite: bool,
    ) -> ClientResult[SPImageItem]:
        """UploadImage operation.

        Args:
            list_title (str):
                listTitle parameter
            image_name (str):
                imageName parameter
            content_stream (bytes):
                contentStream parameter
            list_id (str):
                listId parameter
            item_id (int):
                itemId parameter
            field_id (str):
                fieldId parameter
            overwrite (bool):
                overwrite parameter
        """
        from office365.sharepoint.webs.spimageitem import SPImageItem

        return_type = ClientResult(self.context, SPImageItem())
        qry = ServiceOperationQuery(
            self,
            "UploadImage",
            None,
            {
                "listTitle": list_title,
                "imageName": image_name,
                "contentStream": content_stream,
                "listId": list_id,
                "itemId": item_id,
                "fieldId": field_id,
                "overwrite": overwrite,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type
