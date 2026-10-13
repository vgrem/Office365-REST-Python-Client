from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import IO, TYPE_CHECKING, Any, AnyStr, Callable, Dict, Optional, Union, cast
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import GuidCollection
from office365.runtime.types.odata_property import odata
from office365.sharepoint.changes.collection import ChangeCollection
from office365.sharepoint.changes.log_item_query import ChangeLogItemQuery
from office365.sharepoint.changes.query import ChangeQuery
from office365.sharepoint.changes.token import ChangeToken
from office365.sharepoint.compliance.tags.tag import ComplianceTag
from office365.sharepoint.contenttypes.collection import ContentTypeCollection
from office365.sharepoint.customactions.element_collection import (
    CustomActionElementCollection,
)
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.eventreceivers.definition_collection import (
    EventReceiverDefinitionCollection,
)
from office365.sharepoint.fields.collection import FieldCollection
from office365.sharepoint.fields.creation_information import FieldCreationInformation
from office365.sharepoint.fields.field import Field
from office365.sharepoint.fields.related_field_collection import RelatedFieldCollection
from office365.sharepoint.fields.type import FieldType
from office365.sharepoint.files.checked_out_file_collection import (
    CheckedOutFileCollection,
)
from office365.sharepoint.files.file import File
from office365.sharepoint.flows.connector_result import ConnectorResult
from office365.sharepoint.flows.synchronization_result import FlowSynchronizationResult
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.forms.collection import FormCollection
from office365.sharepoint.listitems.caml.guard import warn_if_unpaged
from office365.sharepoint.listitems.caml.query import CamlQuery
from office365.sharepoint.listitems.collection import ListItemCollection
from office365.sharepoint.listitems.collection_position import (
    ListItemCollectionPosition,
)
from office365.sharepoint.listitems.creation_information import (
    ListItemCreationInformation,
)
from office365.sharepoint.listitems.creation_information_using_path import (
    ListItemCreationInformationUsingPath,
)
from office365.sharepoint.listitems.form_update_value import ListItemFormUpdateValue
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.bloom_filter import ListBloomFilter
from office365.sharepoint.lists.creatables_info import CreatablesInfo
from office365.sharepoint.lists.data_source import ListDataSource
from office365.sharepoint.lists.document_template_type import DocumentTemplateType
from office365.sharepoint.lists.exporter import ExportListProgress
from office365.sharepoint.lists.render_data_parameters import RenderListDataParameters
from office365.sharepoint.lists.rules.rule import SPListRule
from office365.sharepoint.lists.version_policy_manager import VersionPolicyManager
from office365.sharepoint.navigation.configured_metadata_item_col import (
    ConfiguredMetadataNavigationItemCollection,
)
from office365.sharepoint.pages.wiki_page_creation_information import (
    WikiPageCreationInformation,
)
from office365.sharepoint.permissions.securable_object import SecurableObject
from office365.sharepoint.principal.users.user import User
from office365.sharepoint.sharing.object_sharing_settings import ObjectSharingSettings
from office365.sharepoint.sitescripts.utility import SiteScriptUtility
from office365.sharepoint.thresholds import (
    LIST_VIEW_THRESHOLD,
    SAFE_PAGE_SIZE,
    Limits,
    limit,
)
from office365.sharepoint.translation.user_resource import UserResource
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath
from office365.sharepoint.usercustomactions.collection import UserCustomActionCollection
from office365.sharepoint.utilities.utility import Utility
from office365.sharepoint.views.collection import ViewCollection
from office365.sharepoint.views.view import View
from office365.sharepoint.webhooks.subscription_collection import SubscriptionCollection

if TYPE_CHECKING:
    from office365.runtime.converters.dataframe import DataFrameResult
    from office365.runtime.imports import (
        CheckpointStore,
        ImportCheckpoint,
        ImportResult,
    )
    from office365.runtime.operations import ProgressCallback
    from office365.runtime.record_collection import VerificationResult
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.documentmanagement.document_set import DocumentSet
    from office365.sharepoint.documents.contentassemblyfileinfo import (
        ContentAssemblyFileInfo,
    )
    from office365.sharepoint.documents.contentassemblyformanswer import (
        ContentAssemblyFormAnswer,
    )
    from office365.sharepoint.documents.contentassemblymoderntemplatecolumnsmappinginfo import (
        ContentAssemblyModernTemplateColumnsMappingInfo,
    )
    from office365.sharepoint.documents.createhvcsitemapprovalrequestparameters import (
        CreateHVCSItemApprovalRequestParameters,
    )
    from office365.sharepoint.documents.documentgenerationinfo import (
        DocumentGenerationInfo,
    )
    from office365.sharepoint.documents.fieldvalueswithurl import FieldValuesWithUrl
    from office365.sharepoint.documents.itemorderupdatevalue import ItemOrderUpdateValue
    from office365.sharepoint.documents.lockfiledata import LockFileData
    from office365.sharepoint.documents.placeholderv2 import PlaceholderV2
    from office365.sharepoint.documents.publishmoderntemplatepayload import (
        PublishModernTemplatePayload,
    )
    from office365.sharepoint.documents.publishsnippetpayload import (
        PublishSnippetPayload,
    )
    from office365.sharepoint.documents.publishtemplatev2payload import (
        PublishTemplateV2Payload,
    )
    from office365.sharepoint.documents.templatemetadata import TemplateMetaData
    from office365.sharepoint.documents.updatetemplateinfo import UpdateTemplateInfo
    from office365.sharepoint.documents.updatetemplateinfov2 import UpdateTemplateInfoV2
    from office365.sharepoint.files.versionbatchdeleteparameters import (
        FileVersionBatchDeleteParameters,
    )
    from office365.sharepoint.lists.extended_share_point_permission_settings import (
        ExtendedSharePointPermissionSettings,
    )
    from office365.sharepoint.lists.listform import ListForm
    from office365.sharepoint.lists.rules.action import SPRuleAction
    from office365.sharepoint.lists.templatization_metadata import (
        TemplatizationMetaData,
    )
    from office365.sharepoint.permissions.irm.settings import (
        InformationRightsManagementSettings,
    )
    from office365.sharepoint.webs.web import Web
    from office365.sharepoint.workflow.associations.association import (
        WorkflowAssociation,
    )


class List(SecurableObject):
    """
    Represents a list on a SharePoint Web site.

    A container within a SharePoint site that stores list items. A list has a customizable schema that is
    composed of one or more fields.
    """

    def __repr__(self):
        return self.title or self.entity_type_name

    def add_alert(self, title: str, alert_type: int = 1, event_bitmask: int = 1) -> Self:
        """Create an alert on this list for the current user."""

        def _add_alert(url: str | None) -> None:
            from office365.sharepoint.alerts.creation_information import (
                AlertCreationInformation,
            )

            assert url is not None
            params = AlertCreationInformation(
                Title=title,
                AlertType=alert_type,
                EventTypeBitmask=event_bitmask,
                List=url,
            )
            self.context.web.current_user.alerts.add(params)

        self.root_folder.ensure_property("ServerRelativeUrl").after_execute(
            lambda _: _add_alert(self.root_folder.server_relative_url)
        )
        return self

    def export(
        self,
        local_file: IO,
        include_content: bool = False,
        item_exported: Optional[Callable[[ExportListProgress], None]] = None,
    ) -> Self:
        """Export the list as a **package** (``.zip``): per-item JSON + optional content.

        This is the package exporter (``ListExporter``), distinct from the record
        export on :meth:`export_to`/``list.items.export_to``. Run with
        ``execute_query()``:

            >>> with open("Orders.zip", "wb") as f:
            ...     lst.export(f, include_content=True).execute_query()
        """
        from office365.sharepoint.lists.exporter import ListExporter

        return cast(Self, ListExporter.export(self, local_file, include_content, item_exported))

    def can_customize_forms(self) -> ConnectorResult:
        """"""
        from office365.sharepoint.flows.connector_result import ConnectorResult
        from office365.sharepoint.forms.customization import FormsCustomization

        return_type = ConnectorResult(self.context)

        def _can_customize_forms():
            assert self.title is not None
            FormsCustomization.can_customize_forms(self.context, self.title, return_type)

        self.ensure_property("Title").after_execute(lambda _: _can_customize_forms())
        return return_type

    def clear(self) -> Self:
        """Clears the list (deletes all items).

        Loads only the item IDs (paged) and queues a delete per item, so large
        lists are cleared in full. The deletions run on ``execute_batch``:

            >>> target_list.clear().execute_batch()
        """
        self.items.select(["Id"]).get_all().execute_query().delete_all()
        return self

    def create_document_set(self, name: str) -> DocumentSet:
        """
        Creates a DocumentSet (section 3.1.5.3) object on the server.
        """
        from office365.sharepoint.documentmanagement.document_set import DocumentSet

        result = DocumentSet.create(self.context, self.root_folder, name)
        return result

    def create_document_and_get_edit_link(
        self,
        file_name: Optional[str] = None,
        folder_path: Optional[str] = None,
        document_template_type: DocumentTemplateType = DocumentTemplateType.Word,
        template_url: Optional[str] = None,
    ) -> ClientResult[str]:
        """Creates a document at the path and of the type specified within the current list.
        Returns an edit link to the file.

        Args:
            file_name (str): Specifies the name of the document.
            folder_path (str): Specifies the path within the current list to create the document in.
            document_template_type (str): A number representing the type of document to create.
            template_url (str): Specifies the URL of the document template (2) to base the new document on.
        """
        return_type: ClientResult[str] = ClientResult(self.context, str())
        payload = {
            "fileName": file_name,
            "folderPath": folder_path,
            "documentTemplateType": document_template_type.value,
            "templateUrl": template_url,
        }
        qry = ServiceOperationQuery(self, "CreateDocumentAndGetEditLink", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def delete_rule(self, rule_id: str) -> Self:
        """Args:
        rule_id (str):
        """
        payload = {"ruleId": rule_id}
        qry = ServiceOperationQuery(self, "DeleteRule", None, payload)
        self.context.add_query(qry)
        return self

    def get_async_action_config(self) -> ClientResult[Dict]:
        """ """
        return_type = ClientResult[dict](self.context)
        qry = ServiceOperationQuery(self, "GetAsyncActionConfig", return_type=return_type)
        self.context.add_query(qry)
        return return_type

    def get_bloom_filter(self, start_item_id: Optional[int] = None) -> ListBloomFilter:
        """Generates a Bloom filter (probabilistic structure for checking the existence of list items) for the current
            list

        Args:
            start_item_id (int): he ID of the list item to start the search at.
        """
        return_type = ListBloomFilter(self.context)
        payload = {"startItemId": start_item_id}
        qry = ServiceOperationQuery(self, "GetBloomFilter", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_compliance_tag(self) -> ClientResult[ComplianceTag]:
        """ """
        from office365.sharepoint.compliance.store_proxy import SPPolicyStoreProxy

        return_type = ClientResult(self.context, ComplianceTag())

        def _get_compliance_tag(url: str | None):
            assert url is not None
            SPPolicyStoreProxy.get_list_compliance_tag(
                self.context,
                url,
                return_type=return_type,
            )

        self.root_folder.ensure_property("ServerRelativeUrl").after_execute(
            lambda _: _get_compliance_tag(self.root_folder.server_relative_url)
        )
        return return_type

    def set_compliance_tag(
        self,
        compliance_tag_value: str,
        block_delete: Optional[bool] = None,
        block_edit: Optional[bool] = None,
        sync_to_items: Optional[bool] = None,
    ):
        """Apply a retention label ("compliance tag") to a list."""

        def _set_compliance_tag(url: str | None) -> None:
            from office365.sharepoint.compliance.store_proxy import SPPolicyStoreProxy

            assert url is not None
            SPPolicyStoreProxy.set_list_compliance_tag(
                self.context,
                url,
                compliance_tag_value,
                block_delete,
                block_edit,
                sync_to_items,
            )

        self.root_folder.ensure_property("ServerRelativeUrl").after_execute(
            lambda _: _set_compliance_tag(self.root_folder.server_relative_url)
        )
        return self

    def get_metadata_navigation_settings(
        self,
    ) -> ClientResult[ConfiguredMetadataNavigationItemCollection]:
        """Retrieves the configured metadata navigation settings for the list."""
        from office365.sharepoint.navigation.metadata_settings import (
            MetadataNavigationSettings,
        )

        return_type = ClientResult(self.context, ConfiguredMetadataNavigationItemCollection())

        def _loaded():
            assert self.root_folder.server_relative_url is not None
            MetadataNavigationSettings.get_configured_settings(
                self.context, self.root_folder.server_relative_url, return_type
            )

        self.root_folder.ensure_property("ServerRelativeUrl").after_execute(lambda _: _loaded())
        return return_type

    def get_flow_permission_level(self) -> ConnectorResult:
        """"""
        from office365.sharepoint.flows.connector_result import ConnectorResult
        from office365.sharepoint.flows.permissions import FlowPermissions

        return_type = ConnectorResult(self.context)

        def _get_flow_permission_level(title: str | None):
            assert title is not None
            FlowPermissions.get_flow_permission_level_on_list(self.context, title, return_type)

        self.ensure_property("Title").after_execute(lambda _: _get_flow_permission_level(self.title))
        return return_type

    def get_sharing_settings(self) -> ObjectSharingSettings:
        """Retrieves a sharing settings for a List"""
        return_type = ObjectSharingSettings(self.context)

        def _get_sharing_settings():
            from office365.sharepoint.webs.web import Web

            assert self.root_folder.server_relative_url is not None
            list_abs_path = SPResPath.create_absolute(self.context.base_url, self.root_folder.server_relative_url)
            Web.get_object_sharing_settings(self.context, str(list_abs_path), return_type=return_type)

        self.ensure_property("RootFolder").after_execute(lambda _: _get_sharing_settings())
        return return_type

    def get_site_script(self, options: Optional[Dict] = None) -> ClientResult[str]:
        """Creates site script syntax

        Args:
            options (dict or None):
        """
        return_type = ClientResult[str](self.context)

        def _list_loaded():
            assert self.root_folder.server_relative_url is not None
            list_abs_path = SPResPath.create_absolute(self.context.base_url, self.root_folder.server_relative_url)
            SiteScriptUtility.get_site_script_from_list(
                self.context,
                str(list_abs_path),
                options,  # type: ignore[arg-type]
                return_type=return_type,
            )

        self.ensure_property("RootFolder").after_execute(lambda _: _list_loaded())
        return return_type

    def ensure_signoff_status_field(self) -> Field:
        """"""
        return_type = Field(self.context)
        self.fields.add_child(return_type)
        qry = ServiceOperationQuery(self, "EnsureSignoffStatusField", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_all_rules(self) -> ClientResult[ClientValueCollection[SPListRule]]:
        """Retrieves rules of a List"""
        return_type = ClientResult(self.context, ClientValueCollection(SPListRule))
        qry = ServiceOperationQuery(self, "GetAllRules", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_business_app_operation_status(self) -> FlowSynchronizationResult:
        """ """
        return_type = FlowSynchronizationResult(self.context)
        qry = ServiceOperationQuery(self, "GetBusinessAppOperationStatus", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def search_lookup_field_choices(
        self, target_field_name: str, begins_with_search_string: str, paging_info: str
    ) -> FlowSynchronizationResult:
        """Args:
        target_field_name (str):
        begins_with_search_string (str):
        paging_info (str):
        """
        return_type = FlowSynchronizationResult(self.context)
        payload = {
            "targetFieldName": target_field_name,
            "beginsWithSearchString": begins_with_search_string,
            "pagingInfo": paging_info,
        }
        qry = ServiceOperationQuery(self, "SearchLookupFieldChoices", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def sync_flow_callback_url(self, flow_id: str) -> FlowSynchronizationResult:
        """Args:
        flow_id (str):
        """
        return_type = FlowSynchronizationResult(self.context)
        qry = ServiceOperationQuery(self, "SyncFlowCallbackUrl", None, {"flowId": flow_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def sync_flow_instance(self, flow_id: str) -> FlowSynchronizationResult:
        """Args:
        flow_id (str):
        """
        return_type = FlowSynchronizationResult(self.context)
        qry = ServiceOperationQuery(self, "SyncFlowInstance", None, {"flowId": flow_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def sync_flow_instances(self, retrieve_group_flows: bool) -> FlowSynchronizationResult:
        """Args:
        retrieve_group_flows (bool):
        """
        return_type = FlowSynchronizationResult(self.context)
        payload = {"retrieveGroupFlows": retrieve_group_flows}
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

    def create_document_with_default_name(self, folder_path: str, extension: str):
        """Creates a empty document with default filename with the given extension at the path given by folderPath.
        Returns the name of the newly created document.

        Args:
            folder_path (str): The path within the current list at which to create the document.
            extension (str): The file extension without dot prefix.
        """
        return_type: ClientResult[str] = ClientResult[str](self.context)
        payload = {"folderPath": folder_path, "extension": extension}
        qry = ServiceOperationQuery(self, "CreateDocumentWithDefaultName", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def recycle(self, ignore_missing: bool = False) -> ClientResult[str]:
        """Moves the list to the Recycle Bin and returns the identifier of the new Recycle Bin item.

        Args:
            ignore_missing (bool): When True, recycling a list that no longer
                exists (HTTP 404) succeeds instead of raising.
        """
        return_type = ClientResult[str](self.context)
        qry = ServiceOperationQuery(self, "Recycle", None, None, None, return_type)
        self.context.add_query(qry)
        self._tolerate_missing(ignore_missing)
        return return_type

    def start_recycle(self) -> ClientResult[str]:
        """Moves the list to the Recycle Bin and returns the identifier of the new Recycle Bin item."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "StartRecycle", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def render_list_data(self, view_xml: str) -> ClientResult[bytes]:
        """Returns the data for the specified query view. The result is implementation-specific, used for
        providing data to a user interface.

        Args:
            view_xml (str): Specifies the query as XML that conforms to the ViewDefinition type as specified in
                [MS-WSSCAML] section 2.3.2.17.
        """
        return_type = ClientResult[bytes](self.context)
        payload = {"viewXml": view_xml}
        qry = ServiceOperationQuery(self, "RenderListData", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def get_list_data_as_stream(
        context: ClientContext,
        list_full_url: str,
        parameters: Optional[RenderListDataParameters] = None,
        casc_del_warn_message: Optional[str] = None,
        custom_action: Optional[str] = None,
        drill_down: Optional[str] = None,
        field: Optional[str] = None,
        field_internal_name: Optional[str] = None,
        return_type: Optional[ClientResult[bytes]] = None,
    ) -> ClientResult[bytes]:
        """Returns list data from the specified list url and for the specified query parameters.

        Args:
            context (office365.sharepoint.client_context.ClientContext): Client context
            list_full_url (str): The absolute URL of the list.
            parameters (RenderListDataParameters): The parameters to be used.
            casc_del_warn_message (str):
            custom_action (str):
            drill_down (str):
            field (str):
            field_internal_name (str):
            return_type (ClientResult[dict]): The return type.
        """
        if return_type is None:
            return_type = ClientResult(context, bytes())
        payload = {
            "listFullUrl": list_full_url,
            "parameters": parameters,
            "CascDelWarnMessage": casc_del_warn_message,
            "CustomAction": custom_action,
            "DrillDown": drill_down,
            "Field": field,
            "FieldInternalName": field_internal_name,
        }
        qry = ServiceOperationQuery(List(context), "GetListDataAsStream", None, payload, None, return_type, True)
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_onedrive_list_data_as_stream(
        context: ClientContext,
        parameters: Optional[RenderListDataParameters] = None,
        return_type: Optional[ClientResult[bytes]] = None,
    ) -> ClientResult[bytes]:
        """Returns list data from the specified list url and for the specified query parameters.

        Args:
            context (office365.sharepoint.client_context.ClientContext): Client context
            parameters (RenderListDataParameters): The parameters to be used.
            return_type (ClientResult[dict]): The return type.
        """
        if return_type is None:
            return_type = ClientResult(context, bytes())
        payload = {
            "parameters": parameters,
        }
        qry = ServiceOperationQuery(
            List(context),
            "GetOneDriveListDataAsStream",
            None,
            payload,
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    def bulk_validate_update_list_items(
        self,
        item_ids,
        form_values,
        new_document_update=True,
        checkin_comment=None,
        folder_path=None,
    ):
        """Validate and update multiple list items.

        Args:
            item_ids (list[int]): A collection of item Ids that need to be updated with the same formValues.
            form_values (list[ListItemFormUpdateValue]): A collection of field internal names and values for the given
                field. If the collection is empty, no update will take place.
            new_document_update (bool): Indicates whether the list item is a document being updated after upload.
                A value of "true" means yes.
            checkin_comment (str): The comment of check in if any. It's only applicable when the item is checked out.
            folder_path (str): Decoded path of the folder where the items belong to.
                If not provided, the server will try to find items to update under root folder.
        """
        return_type = ClientResult(self.context, ClientValueCollection(ListItemFormUpdateValue))
        params = {
            "itemIds": item_ids,
            "formValues": ClientValueCollection(ListItemFormUpdateValue, form_values),
            "bNewDocumentUpdate": new_document_update,
            "checkInComment": checkin_comment,
            "folderPath": folder_path,
        }
        qry = ServiceOperationQuery(self, "BulkValidateUpdateListItems", None, params, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_lookup_field_choices(self, target_field_name: str, paging_info: Optional[str] = None) -> ClientResult[str]:
        """Retrieves the possible choices or values for a lookup field in a SharePoint list

        Args:
            target_field_name (str):
            paging_info (str):
        """
        return_type = ClientResult(self.context, str())
        params = {"targetFieldName": target_field_name, "pagingInfo": paging_info}
        qry = ServiceOperationQuery(self, "GetLookupFieldChoices", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_list_item_changes_since_token(self, query: ChangeLogItemQuery) -> ClientResult[AnyStr]:
        """
        Returns the changes made to the list since the date and time specified in the change token defined
        by the query input parameter.
        """
        return_type = ClientResult(self.context, bytes())
        payload = {"query": query}
        qry = ServiceOperationQuery(self, "getListItemChangesSinceToken", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type  # type: ignore[return-type]

    def save_as_new_view(self, old_name: str, new_name: str, private_view: bool, uri: str) -> ClientResult[str]:
        """Overwrites a view if it already exists, creates a new view if it does not; and then extracts the
        implementation-specific filter and sort information from the URL and builds and updates the view's XML.
        Returns the URL of the view.

        Args:
            old_name (str): The name of the view the user is currently on.
            new_name (str): The new name given by the user.
            private_view (bool): Set to "true" to make the view private; otherwise, "false".
            uri (str): URL that contains all the implementation-specific filter and sort information for the view.
        """
        payload = {
            "oldName": old_name,
            "newName": new_name,
            "privateView": private_view,
            "uri": uri,
        }
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "SaveAsNewView", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def save_as_template(self, file_name: str, name: str, description: str, save_data: bool) -> Self:
        """Saves the list as a template in the list template gallery and includes the option of saving with or
        without the data that is contained in the current list.

        Args:
            save_data (bool): true to save the data of the original list along with the list template; otherwise, false
            description (str): A string that contains the description for the list template.
            name (str): A string that contains the title for the list template.
            file_name (str): A string that contains the file name for the list template with an .stp extension.
        """
        payload = {
            "strFileName": file_name,
            "strName": name,
            "strDescription": description,
            "bSaveData": save_data,
        }
        qry = ServiceOperationQuery(self, "saveAsTemplate", None, payload, None, None)
        self.context.add_query(qry)
        return self

    def get_item_by_unique_id(self, unique_id: str) -> ListItem:
        """Returns the list item with the specified ID.

        Args:
            unique_id (str): The unique ID that is associated with the list item.
        """
        return ListItem(
            self.context,
            ServiceOperationPath("getItemByUniqueId", [unique_id], self.resource_path),
        )

    def get_web_dav_url(self, source_url: str) -> ClientResult[str]:
        """Gets the trusted URL for opening the folder in Explorer view.

        Args:
            source_url (str): The URL of the current folder the user is in.
        """

        return_type = ClientResult(self.context, str())
        payload = {"sourceUrl": source_url}
        qry = ServiceOperationQuery(self, "getWebDavUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    # def get_files(self) -> ListItemCollection:
    #    """Returns a list of files in the list"""
    #    return self.items.expand(["File"]).get()

    # def get_folders(self) -> ListItemCollection:
    #    """Returns a list of folders in the list"""
    #    return self.items.expand(["Folder"]).get()

    # def validate_broken_taxonomy_values(self) -> Self:
    #    """Clears the broken taxonomy values"""
    #    raise NotImplementedError("validate_broken_taxonomy_values")

    def index_candidates(self, caml_query: CamlQuery) -> list[str]:
        """The columns a CAML query filters/sorts on that are worth indexing (``ID`` excluded).

        A starting point for :meth:`ensure_indexed` — indexing is explicit and the
        build runs in the background. Shorthand for ``caml_query.index_candidates``.
        """
        return caml_query.index_candidates

    def check_query(self, caml_query: CamlQuery, *, item_count: Optional[int] = None) -> None:
        """Pre-flight a CAML query against the SharePoint list view threshold.

        Loads the list's item count (unless ``item_count`` is given) and the
        ``Indexed`` status of the columns the query filters/sorts on, and raises
        :class:`~office365.sharepoint.exceptions.SPQueryThrottledException` — with
        the exact columns to index — when the query would be throttled, instead of
        letting the server return an opaque 500. Performs 1-2 requests.

        Args:
            caml_query: The query to check.
            item_count: The list size, when already known (avoids a request).
        """
        from office365.sharepoint.exceptions import SPQueryThrottledException

        if item_count is None:
            self.ensure_property("ItemCount").execute_query()
            item_count = self.item_count or 0
        if item_count <= LIST_VIEW_THRESHOLD:
            return
        candidates = set(caml_query.index_candidates)
        if not candidates:
            return

        fields = self.fields
        fields.select(["InternalName", "Title", "Indexed"]).get().execute_query()
        not_indexed = sorted(
            str(f.internal_name or f.title or "")
            for f in fields
            if (f.internal_name in candidates or f.title in candidates) and f.indexed is not True
        )
        if not_indexed:
            names = ", ".join(repr(name) for name in not_indexed)
            raise SPQueryThrottledException(
                f"This CAML query filters/sorts on non-indexed column(s) {names} and the list has "
                f"{item_count:,} items (over the {LIST_VIEW_THRESHOLD:,}-item list view threshold), so it "
                f"would be throttled. Index them first, e.g. "
                f"lst.ensure_indexed({not_indexed[0]!r}).execute_query(), or filter on ID (always indexed)."
            )

    @limit(Limits.LIST_VIEW, arg="page_size")
    def get_items(
        self,
        caml_query: Optional[CamlQuery] = None,
        page_size: Optional[int] = None,
        check: bool = False,
    ) -> ListItemCollection:
        """Returns a collection of items from the list based on the specified query.

        Pass ``page_size`` to page the results (continues from the last item via
        ``ListItemCollectionPosition``), so a query over more than the 5,000-item
        list view threshold can be read in full:

            >>> for item in list.get_items(query, page_size=2000).execute_query():
            ...     ...

        Pass ``check=True`` to pre-flight the query with :meth:`check_query` first
        (raises actionable guidance instead of an opaque server 500). It performs
        1-2 requests immediately, so it is off by default.
        """
        if not caml_query:
            caml_query = CamlQuery.create_all_items_query()
        if check:
            self.check_query(caml_query)
        if page_size is None:
            warn_if_unpaged(caml_query, item_count=self.item_count)
        return_type = ListItemCollection(self.context, self.items.resource_path)
        payload = {"query": caml_query}
        qry = ServiceOperationQuery(self, "GetItems", None, payload, None, return_type)
        self.context.add_query(qry)
        if page_size:
            return_type.paged(page_size)

            def _next_page() -> None:
                # CAML paging: continue from the last item via its collection position,
                # carrying the sort columns (then ID) so the next page starts where
                # the previous one stopped.
                last = return_type[-1]
                parts = ["Paged=TRUE"]
                parts.extend(
                    f"p_{name}={last.properties.get(name)}"
                    for name in caml_query.order_by_fields
                    if name.upper() != "ID"
                )
                parts.append(f"p_ID={last.id}")
                caml_query.ListItemCollectionPosition = ListItemCollectionPosition(PagingInfo="&".join(parts))
                next_qry = ServiceOperationQuery(self, "GetItems", None, {"query": caml_query}, None, return_type)
                self.context.add_query(next_qry)

            return_type._next_page = _next_page
        return return_type

    def ensure_field(
        self,
        name: "str | FieldCreationInformation",
        field_type: FieldType = FieldType.Text,
        description: str | None = None,
        *,
        on_conflict: str = "skip",
    ) -> Field:
        """Ensure a single column exists on the list, creating it if missing.

        Pass a column ``name`` for a basic column — with an optional ``field_type``
        and ``description`` — or a populated :class:`FieldCreationInformation` for
        a rich one (``Choices`` for Choice/MultiChoice, ``Formula`` for Calculated,
        ``Required``, ``LookupListId``/``LookupFieldName`` for Lookup, ...)::

            lst.ensure_field("Status", FieldType.Choice)
            lst.ensure_field(
                FieldCreationInformation(Title="Status", FieldTypeKind=FieldType.Choice, Choices=["A", "B"])
            )

        The check is deferred — the column is looked up and created when the
        caller executes the query (e.g. ``list.ensure_field("Status").execute_query()``).
        With ``on_conflict="update"`` an existing column's type/description and rich
        settings (choices, formula, required) are reconciled.

        Args:
            name: The column title, or a ``FieldCreationInformation`` describing it.
            field_type: The field type to create it with if missing (Text by default).
            description: The description of the column.
            on_conflict: ``"skip"`` (default) or ``"update"``.

        Returns:
            Field: The existing or newly created field.
        """
        if isinstance(name, FieldCreationInformation):
            info = name
        else:
            info = FieldCreationInformation(Title=name, FieldTypeKind=field_type, Description=description)
        return self.fields.ensure(info, on_conflict=on_conflict)

    def ensure_fields(
        self,
        columns: "Mapping[str, FieldType] | Sequence[str | FieldCreationInformation]",
        *,
        on_conflict: str = "skip",
    ) -> list[Field]:
        """Ensure the specified columns exist on the list, creating missing ones.

        Reconciles the source schema with the target list before data import:
        existing fields are kept (or reconciled with ``on_conflict="update"``),
        missing ones are created (Text by default). Deferred — execute the query
        after.

        Args:
            columns: A mapping of field name -> :class:`FieldType` (basic columns),
                or a sequence of names (created as Text) and/or
                :class:`FieldCreationInformation` specs for rich columns
                (choice/lookup/calculated/...).
            on_conflict: ``"skip"`` (default) or ``"update"``.

        Returns:
            list[Field]: The existing or newly created fields.
        """
        if isinstance(columns, Mapping):
            return [self.ensure_field(name, field_type, on_conflict=on_conflict) for name, field_type in columns.items()]
        return [self.ensure_field(column, on_conflict=on_conflict) for column in columns]

    def ensure_indexed(self, name: str) -> Field:
        """Enable the index on an existing column (idempotent, deferred).

        Indexing the columns used in a CAML/``$filter``/``$orderby`` lets queries
        filter and sort past the 5,000-item list view threshold. The column must
        already exist. Run with ``execute_query()``:

            >>> lst.ensure_indexed("Status").execute_query()
        """
        return self.fields.get_by_internal_name_or_title(name).ensure_indexed()

    def from_records(
        self,
        source,
        *,
        format: str = "records",  # noqa: A002
        schema: "Dict[str, FieldType] | None" = None,
        chunksize: int = SAFE_PAGE_SIZE,
        progress: "ProgressCallback | None" = None,
        total: "int | None" = None,
        checkpoint: "ImportCheckpoint | CheckpointStore | str | None" = None,
        on_error: str = "raise",
        key: "str | list[str] | None" = None,
        key_field: str = "MigrationKey",
        on_conflict: str = "skip",
        enforce_unique: bool = False,
        dry_run: bool = False,
        on_schema_change: str = "evolve",
        dead_letter: "str | None" = None,
        mapping: "Dict[str, str] | None" = None,
    ) -> "ImportResult":
        """Stream a source into this list's items, memory-bounded (streaming entry).

        Returns an :class:`~office365.runtime.imports.ImportResult`; run it with
        ``execute_query()`` (sequential) or ``execute_batch(...)`` (batched):

            >>> lst.from_dataframe(pd.read_csv(url, chunksize=2000)).execute_batch(concurrency=5)

        Fields are provisioned from the first chunk (or ``schema``) for the
        ``dataframe``/``csv`` formats; columns that first appear in a later chunk
        are added (``on_schema_change="evolve"``, the default) or rejected
        (``"fail"``). Column names are sanitized into field internal names; NaN
        cells are skipped. ``checkpoint`` resumes; ``key`` makes it idempotent.

        Args:
            source: A DataFrame / chunk iterable / CSV path (``dataframe``/``csv``),
                record batches (``records``), or a reader source for other formats.
            format: Source format (default ``"records"``).
            schema: Optional explicit ``{column: FieldType}``; inferred from dtypes.
                A ``FieldType`` also drives typed value coercion (multi-choice,
                lookup, user, URL, geolocation, ...).
            chunksize: Rows per chunk for a DataFrame/CSV source.
            progress: Optional hook fired live (initial, per chunk, per batch).
            total: Total rows when known upfront (drives the progress percentage).
            checkpoint: Optional resumable-run checkpoint (object or path).
            on_error: ``"raise"`` (default) or ``"collect"``.
            key: Natural-key source column(s) for idempotency; ``None`` disables it.
            key_field: Target column storing the derived key hash.
            on_conflict: ``"skip"`` (default) or ``"update"``.
            enforce_unique: Mark the key column unique (guards a create race).
            dry_run: Plan the create/update/skip counts without writing.
            on_schema_change: ``"evolve"`` (default) or ``"fail"``.
            mapping: Optional ``{source_column: target_name}`` rename map.
            dead_letter: Optional JSONL path for collected chunk failures.

        Returns:
            ImportResult: The deferred streaming import driver.
        """
        from functools import partial

        from office365.runtime.converters.dataframe import records_from_dataframe
        from office365.sharepoint.fields.coercion import coerce_field_value
        from office365.sharepoint.fields.name import internal_field_name

        if on_schema_change not in ("evolve", "fail"):
            raise ValueError(f"on_schema_change must be 'evolve' or 'fail', got {on_schema_change!r}")
        provisioned: set[str] = set()
        coercions: "Dict[str, Any] | None" = None
        if isinstance(schema, dict):
            coercions = {
                internal_field_name(str(column)): partial(coerce_field_value, field_type)
                for column, field_type in schema.items()
            }

        def _mapped(chunk: Any) -> Any:
            if mapping and hasattr(chunk, "rename"):
                return chunk.rename(columns=mapping)
            return chunk

        def _ensure_new_fields(chunk: Any) -> None:
            chunk = _mapped(chunk)
            if not hasattr(chunk, "columns"):  # only DataFrame/CSV chunks carry a schema
                return
            new = [c for c in chunk.columns if internal_field_name(str(c)) not in provisioned]
            if not new:
                return
            if on_schema_change == "fail" and provisioned:
                raise ValueError(f"source schema changed: new column(s) {new}")
            self.fields.ensure_from_dataframe(chunk[new])
            provisioned.update(internal_field_name(str(c)) for c in new)
            self.context.execute_query()

        def _prepare(first_chunk: Any) -> None:
            if schema is not None:
                self.ensure_fields(schema)
                names = schema.keys() if isinstance(schema, dict) else schema
                provisioned.update(internal_field_name(str(k)) for k in names)
            else:
                _ensure_new_fields(first_chunk)

        def _to_records(chunk: Any) -> list[dict]:
            return records_from_dataframe(_mapped(chunk), key_fn=internal_field_name)

        to_records = _to_records if format in ("dataframe", "csv") else None

        return self.items.from_records(
            source,
            format=format,
            chunksize=chunksize,
            total=total,
            key=key,
            key_field=key_field,
            on_conflict=on_conflict,
            enforce_unique=enforce_unique,
            checkpoint=checkpoint,
            on_error=on_error,
            progress=progress,
            prepare=_prepare,
            before_chunk=_ensure_new_fields,
            to_records=to_records,
            dry_run=dry_run,
            dead_letter=dead_letter,
            mapping=mapping if to_records is None else None,
            coerce=coercions,
        )

    def from_dataframe(self, source, **opts) -> "ImportResult":
        """Stream a DataFrame / chunked CSV into this list (see :meth:`from_records`)."""
        return self.from_records(source, format="dataframe", **opts)

    def from_csv(self, source, **opts) -> "ImportResult":
        """Stream a CSV source into this list (see :meth:`from_records`)."""
        return self.from_records(source, format="csv", **opts)

    def from_json(self, source, **opts) -> "ImportResult":
        """Stream a JSON-array file into this list (see :meth:`from_records`)."""
        return self.from_records(source, format="json", **opts)

    def from_ndjson(self, source, **opts) -> "ImportResult":
        """Stream an NDJSON source into this list (see :meth:`from_records`)."""
        return self.from_records(source, format="ndjson", **opts)

    def from_excel(self, source, **opts) -> "ImportResult":
        """Stream an Excel (.xlsx) worksheet into this list (see :meth:`from_records`)."""
        return self.from_records(source, format="excel", **opts)

    def from_parquet(self, source, **opts) -> "ImportResult":
        """Stream a Parquet file into this list (see :meth:`from_records`)."""
        return self.from_records(source, format="parquet", **opts)

    def from_orc(self, source, **opts) -> "ImportResult":
        """Stream an ORC file into this list (see :meth:`from_records`)."""
        return self.from_records(source, format="orc", **opts)

    def from_feather(self, source, **opts) -> "ImportResult":
        """Stream a Feather file into this list (see :meth:`from_records`)."""
        return self.from_records(source, format="feather", **opts)

    def from_file(
        self,
        server_relative_url: str,
        *,
        format: str = "csv",  # noqa: A002
        chunksize: int = SAFE_PAGE_SIZE,
        **opts,
    ) -> "ImportResult":
        """Stream a SharePoint-hosted file (CSV/XLSX) into this list's items.

        Downloads the file from this site (honoring auth) and streams it through
        :meth:`from_records` — bounded memory, resumable and idempotent with
        ``key=...``. ``format`` is ``"csv"`` (default) or ``"xlsx"``/``"excel"``.

            >>> lst.from_file("Shared Documents/stocks.csv", key=["Name", "date"]) \\
            ...    .execute_batch(concurrency=5)
        """
        import io

        file = self.context.web.get_file_by_server_relative_url(server_relative_url)
        content = file.read()
        if format in ("xlsx", "excel"):
            from office365.runtime.converters.dataframe import require_pandas

            df = require_pandas().read_excel(io.BytesIO(content))
            return self.from_dataframe(df, chunksize=chunksize, **opts)
        return self.from_csv(io.BytesIO(content), chunksize=chunksize, **opts)

    def queue_dataframe(
        self,
        df,
        schema: "Dict[str, FieldType] | None" = None,
        progress: "ProgressCallback | None" = None,
    ) -> Self:
        """Queue a DataFrame into this list **deferred** (queue-all).

        Provisions the columns (from the dtypes, or ``schema``) and queues an item
        create per row; run with ``execute_query()``. For large frames use the
        streaming :meth:`from_dataframe` (bounded memory + idempotency).
        """
        if schema is not None:
            self.ensure_fields(schema)
        else:
            self.fields.ensure_from_dataframe(df)
        self.items.queue_dataframe(df, progress=progress)
        return self

    def queue_records(self, records, progress: "ProgressCallback | None" = None) -> Self:
        """Queue record dicts into this list's items (deferred)."""
        self.items.queue_records(records, progress=progress)
        return self

    def verify(
        self,
        source,
        *,
        key: "str | list[str]",
        format: str = "dataframe",  # noqa: A002
        key_field: str = "MigrationKey",
    ) -> "VerificationResult":
        """Reconcile a source's natural keys against this list (bounded).

        Streams the source, hashes each row's natural key and checks it against the
        list's existing keys. ``format`` is ``"dataframe"`` (default), ``"csv"`` or
        any registered format.
        """
        from office365.runtime.converters.dataframe import records_from_dataframe
        from office365.sharepoint.fields.name import internal_field_name

        def _to_records(chunk):
            return records_from_dataframe(chunk, key_fn=internal_field_name)

        to_records = _to_records if format in ("dataframe", "csv") else None
        return self.items.verify(source, key=key, format=format, key_field=key_field, to_records=to_records)

    def export_to(self, target, *, format: str = "csv", page_size=None, **opts) -> Self:  # noqa: A002
        """Export this list's items to ``target`` in ``format`` (deferred).

        The record exporter (CSV/NDJSON/JSON/Excel); pass ``page_size`` to stream
        an appendable format page by page (bounded memory). For the ``.zip``
        package export use :meth:`export`. Run with ``execute_query()``.
        """
        if page_size:
            self.items.export_to(target, format=format, page_size=page_size, **opts)
        else:
            self.items.get_all().export_to(target, format=format, **opts)
        return self

    async def export_to_async(self, target, *, format: str = "csv", page_size=None, **opts) -> Self:  # noqa: A002
        """Async twin of :meth:`export_to`.

        The list's items are paged and written on the worker pool, so the event
        loop stays free; pass ``page_size`` to stream an appendable format page by
        page (bounded memory) or omit it to load and write the whole collection.

            >>> await lst.export_to_async("items.csv", page_size=2000)
        """
        items = self.items
        if page_size:
            await items.export_to_async(target, format=format, page_size=page_size, **opts)
        else:
            # `List.items` builds a new collection per access, so keep one
            # reference: load it, then export the loaded items.
            await items.get_all_async()
            await items.export_to_async(target, format=format, **opts)
        return self

    def to_dataframe(self) -> "DataFrameResult":
        """Export this list's items to a pandas DataFrame (deferred result)."""
        return self.items.get_all().to_dataframe()

    def to_parquet(self, target) -> Self:
        """Export this list's items to Parquet (deferred; requires the ``[parquet]`` extra)."""
        return self.export_to(target, format="parquet")

    def to_orc(self, target) -> Self:
        """Export this list's items to ORC (deferred; requires the ``[parquet]`` extra)."""
        return self.export_to(target, format="orc")

    def to_feather(self, target) -> Self:
        """Export this list's items to Feather (deferred; requires the ``[parquet]`` extra)."""
        return self.export_to(target, format="feather")

    def add_item(self, creation_information: Union[ListItemCreationInformation, Dict]) -> ListItem:
        """The recommended way to add a list item is to send a POST request to the ListItemCollection resource endpoint,
        as shown in ListItemCollection request examples."""
        return_type = ListItem(self.context, None, self)
        self.items.add_child(return_type)
        if isinstance(creation_information, dict):
            for k, v in creation_information.items():
                return_type.set_property(k, v, True)
            return_type.ensure_type_name(self)
            qry = ServiceOperationQuery(self, "items", None, return_type, None, return_type)
            self.context.add_query(qry)
        else:

            def _add_item():
                assert self.root_folder.server_relative_url is not None
                creation_information.FolderUrl = self.context.base_url + self.root_folder.server_relative_url
                payload = {"parameters": creation_information}
                next_qry = ServiceOperationQuery(self, "addItem", None, payload, None, return_type)
                self.context.add_query(next_qry)

            self.root_folder.ensure_property("ServerRelativeUrl").after_execute(lambda _: _add_item())
        return return_type

    def create_wiki_page(self, page_name: str, page_content: str) -> File:
        """Creates a wiki page.

        Args:
            page_name (str):
            page_content (str):
        """
        return_type = File(self.context)
        self.root_folder.files.add_child(return_type)

        def _create_wiki_page(url: str | None):
            assert url is not None
            page_url = "/".join([url, page_name])
            wiki_props = WikiPageCreationInformation(ServerRelativeUrl=page_url, WikiHtmlContent=page_content)
            Utility.create_wiki_page_in_context_web(self.context, wiki_props, return_type)

        self.root_folder.ensure_property("ServerRelativeUrl").after_execute(
            lambda f: _create_wiki_page(f.server_relative_url)
        )
        return return_type

    def add_item_using_path(self, leaf_name: str, object_type: int, folder_url: str) -> ListItem:
        """Adds a ListItem to an existing List.

        Args:
            leaf_name (str): Specifies the name of the list item that will be created.
                In the case of a document library, the name is equal to the filename of the list item.
            object_type (int): Specifies the file system object type for the item that will be created.
                It MUST be either FileSystemObjectType.File or FileSystemObjectType.Folder.
            folder_url (str ot None): Specifies the url of the folder of the new list item.
                The value MUST be either null or the decoded url value an empty string or a server-relative URL or an
                    absolute URL. If the value is not null or the decoded url value not being empty string, the decoded
                    url value MUST point to a location within the list.
        """
        parameters = ListItemCreationInformationUsingPath(leaf_name, object_type, FolderPath=folder_url)
        return_type = ListItem(self.context)
        payload = {"parameters": parameters}
        qry = ServiceOperationQuery(self, "AddItemUsingPath", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_validate_update_item(
        self, create_info: ListItemCreationInformation, form_values: Optional[Dict] = None
    ) -> ClientResult[ClientValueCollection[ListItemFormUpdateValue]]:
        """Adds an item to an existing list and validate the list item update values. If all fields validated
            successfully,
        commit all changes. If there's any exception in any of the fields, the item will not be committed.

        Args:
            create_info (ListItemCreationInformation): Contains the information that determines how the item will be
                created.
            form_values (dict): A collection of field internal names and values for the given field.
                If the collection is empty, no update will take place.
        """
        assert form_values is not None
        payload = {
            "listItemCreateInfo": create_info,
            "formValues": [ListItemFormUpdateValue(k, v) for k, v in form_values.items()],
        }
        return_type = ClientResult(self.context, ClientValueCollection(ListItemFormUpdateValue))
        qry = ServiceOperationQuery(self, "AddValidateUpdateItem", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_item_by_id(self, item_id: int) -> ListItem:
        """Returns the list item with the specified list item identifier."""
        return ListItem(
            self.context,
            ServiceOperationPath("getItemById", [item_id], self.resource_path),
        )

    def get_item_by_url(self, url: str) -> ListItem:
        """Returns the list item with the specified site or server relative url."""
        return_type = ListItem(self.context)
        self.items.add_child(return_type)

        def _after_loaded(item):
            return_type.copy_from(item)

        def _get_item_by_url():
            assert self.root_folder.server_relative_url is not None
            path = os.path.join(self.root_folder.server_relative_url, url)
            self.items.get_by_url(path).after_execute(_after_loaded, execute_first=True)

        self.ensure_property("RootFolder").after_execute(lambda _: _get_item_by_url())
        return return_type

    def get_view(self, view_id: str) -> View:
        """Returns the list view with the specified view identifier.

        Args:
            view_id (str):
        """
        return View(
            self.context,
            ServiceOperationPath("getView", [view_id], self.resource_path),
            self,
        )

    def get_changes(self, query: Optional[ChangeQuery] = None) -> ChangeCollection:
        """Returns the collection of changes from the change log that have occurred within the list,
        based on the specified query.

        Args:
            query (ChangeQuery): Specifies which changes to return
        """
        if query is None:
            query = ChangeQuery(List=True)
        return_type = ChangeCollection(self.context)
        payload = {"query": query}
        qry = ServiceOperationQuery(self, "getChanges", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_checked_out_files(self) -> CheckedOutFileCollection:
        """Returns a collection of checked-out files as specified in section 3.2.5.381."""
        return_type = CheckedOutFileCollection(
            self.context,
            ServiceOperationPath("GetCheckedOutFiles", None, self.resource_path),
        )
        qry = ServiceOperationQuery(self, "GetCheckedOutFiles", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def render_list_data_as_stream(
        self,
        view_xml: Optional[str] = None,
        render_options: Optional[int] = None,
        expand_groups: Optional[bool] = None,
    ) -> ClientResult[bytes]:
        """Returns the data for the specified query view.

        Args:
            view_xml (str): Specifies the CAML view XML.
            render_options (int): Specifies the type of output to return.
            expand_groups (bool): Specifies whether to expand the grouping or not.
        """
        return_type = ClientResult(self.context, bytes())
        if view_xml is None:
            view_xml = "<View/>"
        payload = {
            "parameters": RenderListDataParameters(
                ViewXml=view_xml,
                RenderOptions=render_options,
                ExpandGroups=expand_groups,
            ),
        }
        qry = ServiceOperationQuery(self, "RenderListDataAsStream", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def reserve_list_item_id(self) -> ClientResult[int]:
        """Reserves the returned list item identifier for the idempotent creation of a list item."""
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "ReserveListItemId", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_related_fields(self) -> RelatedFieldCollection:
        """
        Returns a collection of lookup fields that use this list as a data source and
        that have FieldLookup.IsRelationship set to true.
        """
        return RelatedFieldCollection(
            self.context,
            ServiceOperationPath("getRelatedFields", [], self.resource_path),
        )

    def get_special_folder_url(
        self, folder_type: int, force_create: bool, existing_folder_guid: str
    ) -> ClientResult[str]:
        """Gets the relative URL of the Save to OneDrive folder.

        Args:
            folder_type (int): The Save-to-OneDrive type.
            force_create (bool): Specify true if the folder doesn't exist and SHOULD be created.
            existing_folder_guid (str): The GUID of the created folders that exist, if any.
        """
        payload = {
            "type": folder_type,
            "bForceCreate": force_create,
            "existingFolderGuid": existing_folder_guid,
        }
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetSpecialFolderUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def reset_doc_ids(self) -> Self:
        """

        Performs the same function as ResetDocIdByServerRelativePath (section 3.1.5.10.2.1.1), but for every
        document in the specified document library.
        """
        from office365.sharepoint.documentmanagement.document_id import DocumentId

        def _reset_doc_ids(url: str | None) -> None:
            assert url is not None
            doc_mng = DocumentId(self.context)
            doc_mng.reset_doc_ids_in_library(url)

        self.ensure_property("RootFolder").after_execute(lambda _: _reset_doc_ids(self.root_folder.server_relative_url))
        return self

    def set_exempt_from_block_download_of_non_viewable_files(self, value: bool) -> Self:
        """
        Method to set the ExemptFromBlockDownloadOfNonViewableFiles property.
        Ensures that only a tenant administrator can set the exemption.
        """
        qry = ServiceOperationQuery(
            self,
            "SetExemptFromBlockDownloadOfNonViewableFiles",
            [value],
            None,
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    @property
    def id(self) -> Optional[str]:
        """Gets a value that specifies the list identifier."""
        return self.properties.get("Id", None)

    @property
    def additional_ux_properties(self) -> Optional[str]:
        return self.properties.get("AdditionalUXProperties", None)

    @property
    def author(self) -> User:
        """Specifies the user who created the list."""
        return self.properties.get("Author", User(self.context, ResourcePath("Author", self.resource_path)))

    @property
    def allow_content_types(self) -> Optional[bool]:
        """Specifies whether the list supports content types."""
        return self.properties.get("AllowContentTypes", None)

    @property
    def allow_deletion(self) -> Optional[bool]:
        """Specifies whether the list could be deleted."""
        return self.properties.get("AllowDeletion", None)

    @property
    def hidden(self) -> Optional[bool]:
        """Specifies whether the list is hidden from UI."""
        return self.properties.get("Hidden", None)

    @property
    def base_template(self) -> Optional[int]:
        """Specifies the list server template of the list."""
        return self.properties.get("BaseTemplate", None)

    @property
    def base_type(self) -> Optional[int]:
        """
        Specifies the base type of the list.
        It MUST be one of the following values: GenericList, DocumentLibrary, DiscussionBoard, Survey, or Issue.
        """
        return self.properties.get("BaseType", None)

    @property
    def browser_file_handling(self) -> Optional[int]:
        """
        Specifies the override at the list level for the BrowserFileHandling property of the Web application.
        If the BrowserFileHandling property of the Web application is BrowserFileHandling.Strict,
        then this setting MUST be ignored. If the BrowserFileHandling property of the Web application is
        BrowserFileHandling.Permissive, then this setting MUST be respected.
        """
        return self.properties.get("BrowserFileHandling", None)

    @property
    def created(self) -> datetime:
        """Specifies when the list was created."""
        return self.properties.get("Created", datetime.min)

    @property
    def default_display_form_url(self) -> Optional[str]:
        """Specifies the location of the default display form for the list."""
        return self.properties.get("DefaultDisplayFormUrl", None)

    @odata(name="DefaultViewPath")
    @property
    def default_view_path(self) -> SPResPath:
        """Specifies the server-relative URL of the default view for the list."""
        return self.properties.get("DefaultViewPath", SPResPath())

    @property
    def default_view_url(self) -> Optional[str]:
        """
        Specifies the server-relative URL of the default view for the list.
        """
        return self.properties.get("DefaultViewUrl", None)

    @property
    def crawl_non_default_views(self) -> Optional[bool]:
        """
        Specifies whether or not the crawler indexes the non-default views of the list.
        Specify a value of true if the crawler indexes the list's non-default views; specify false if otherwise.
        """
        return self.properties.get("CrawlNonDefaultViews", None)

    @odata(name="CreatablesInfo")
    @property
    def creatables_info(self) -> CreatablesInfo:
        """
        Returns an object that describes what this list can create, and a collection of links to visit in order to
        create those things. If it can't create certain things, it contains an error message describing why.

         The consumer MUST append the encoded URL of the current page to the links returned here.
         (This page the link goes to needs it as a query parameter to function correctly.)
         The consumer SHOULD also consider appending &IsDlg=1 to the link, to remove the UI from the linked page,
         if desired.
        """
        return self.properties.get(
            "CreatablesInfo",
            CreatablesInfo(self.context, ResourcePath("CreatablesInfo", self.resource_path)),
        )

    @odata(name="CurrentChangeToken")
    @property
    def current_change_token(self) -> ChangeToken:
        """Gets the current change token that is used in the change log for the list."""
        return self.properties.get("CurrentChangeToken", ChangeToken())

    @odata(name="DataSource")
    @property
    def data_source(self) -> ListDataSource:
        """
        Specifies the data source of an external list.
        If HasExternalDataSource is "false", the server MUST return NULL.
        """
        return self.properties.get("DataSource", ListDataSource())

    @property
    def default_edit_form_url(self) -> Optional[str]:
        """Gets a value that specifies the URL of the edit form to use for list items in the list."""
        return self.properties.get("DefaultEditFormUrl", None)

    @property
    def default_item_open_in_browser(self) -> Optional[bool]:
        return self.properties.get("DefaultItemOpenInBrowser", None)

    @property
    def default_item_open_use_list_setting(self) -> Optional[bool]:
        """
        This property returns whether to use the List setting or the server wide setting for
        DefaultItemOpen (BrowserEnabledDocuments setting) in the Web application. This property can only be set to
        false, thereby using the server-wide setting. To set it to use List setting, set the value for DefaultItemOpen.
        """
        return self.properties.get("DefaultItemOpenUseListSetting", None)

    @property
    def disable_commenting(self) -> Optional[bool]:
        return self.properties.get("DisableCommenting", None)

    @property
    def disable_grid_editing(self) -> Optional[bool]:
        return self.properties.get("DisableGridEditing", None)

    @property
    def document_template_url(self) -> Optional[str]:
        """Specifies the URL of the document template assigned to the list."""
        return self.properties.get("DocumentTemplateUrl", None)

    @odata(name="EffectiveBasePermissions")
    @property
    def effective_base_permissions(self):
        """
        Specifies the effective permissions on the list that are assigned to the current user.
        """
        from office365.sharepoint.permissions.base_permissions import BasePermissions

        return self.properties.get("EffectiveBasePermissions", BasePermissions())

    @odata(name="EffectiveBasePermissionsForUI")
    @property
    def effective_base_permissions_for_ui(self):
        """
        Specifies the effective base permissions for the current user as they SHOULD be displayed in user interface (UI)
        If the list is not in read-only UI mode, the value of EffectiveBasePermissionsForUI MUST be the same as the
        value of EffectiveBasePermissions (section 3.2.5.79.1.1.17). If the list is in read-only UI mode, the value
        of EffectiveBasePermissionsForUI MUST be a subset of the value of EffectiveBasePermissions.
        """
        from office365.sharepoint.permissions.base_permissions import BasePermissions

        return self.properties.get("EffectiveBasePermissionsForUI", BasePermissions())

    @property
    def enable_assign_to_email(self) -> Optional[bool]:
        """
        Gets or sets a Boolean value specifying whether e-mail notification is enabled for the list.
        """
        return self.properties.get("EnableAssignToEmail", None)

    @property
    def enable_attachments(self) -> Optional[bool]:
        """Specifies whether list item attachments are enabled for the list"""
        return self.properties.get("EnableAttachments", None)

    @property
    def enable_folder_creation(self) -> Optional[bool]:
        """Specifies whether new list folders can be added to the list."""
        return self.properties.get("EnableFolderCreation", None)

    @enable_folder_creation.setter
    def enable_folder_creation(self, value: bool) -> None:
        self.set_property("EnableFolderCreation", value, True)

    @property
    def enable_minor_versions(self) -> Optional[bool]:
        """Specifies whether minor versions are enabled for the list."""
        return self.properties.get("EnableMinorVersions", None)

    @property
    def enable_moderation(self) -> Optional[bool]:
        """Specifies whether content approval is enabled for the list."""
        return self.properties.get("EnableModeration", None)

    @property
    def enable_request_sign_off(self) -> Optional[bool]:
        return self.properties.get("EnableRequestSignOff", None)

    @property
    def enable_versioning(self) -> Optional[bool]:
        """Specifies whether content approval is enabled for the list."""
        return self.properties.get("EnableVersioning", None)

    @property
    def exclude_from_offline_client(self) -> Optional[bool]:
        """
        This doesn't block sync but acts as a recommendation to the client to not take this list offline.
        This gets returned as part of list properties in GetListSchema soap call.
        """
        return self.properties.get("ExcludeFromOfflineClient", None)

    @property
    def exempt_from_block_download_of_non_viewable_files(self) -> Optional[bool]:
        """
        Property indicating whether the list is exempt from the policy to block download of non-server handled files.
        This SHOULD be set using the SetExemptFromBlockDownloadOfNonViewableFiles (section 3.2.5.79.2.1.25) method.
        """
        return self.properties.get("ExemptFromBlockDownloadOfNonViewableFiles", None)

    @property
    def file_save_post_processing_enabled(self) -> Optional[bool]:
        """
        Specifies whether or not the files in the list can be processed in asynchronous manner
        Specify a value of true if the list files can be processed asynchronously; specify false if otherwise.
        """
        return self.properties.get("FileSavePostProcessingEnabled", None)

    @property
    def force_checkout(self) -> Optional[bool]:
        """Specifies whether check out is required when adding or editing documents in the list"""
        return self.properties.get("ForceCheckout", None)

    @property
    def has_content_assembly_templates(self) -> Optional[bool]:
        """ """
        return self.properties.get("HasContentAssemblyTemplates", None)

    @property
    def has_external_data_source(self) -> Optional[bool]:
        """
        Specifies whether the list is an external list.
        """
        return self.properties.get("HasExternalDataSource", None)

    @property
    def has_folder_coloring_fields(self) -> Optional[bool]:
        """ """
        return self.properties.get("HasFolderColoringFields", None)

    @property
    def irm_enabled(self) -> Optional[bool]:
        """Gets a Boolean value that specifies whether Information Rights Management (IRM) is enabled for the list."""
        return self.properties.get("IrmEnabled", None)

    @property
    def irm_expire(self) -> Optional[bool]:
        """Gets a Boolean value that specifies whether Information Rights Management (IRM) expiration is enabled
        for the list
        """
        return self.properties.get("IrmExpire", None)

    @property
    def items(self) -> ListItemCollection:
        """Get list items"""
        return self.properties.get(
            "Items",
            ListItemCollection(self.context, ResourcePath("items", self.resource_path), parent=self),
        )

    @odata(name="RootFolder")
    @property
    def root_folder(self) -> Folder:
        """Get a root folder"""
        return self.properties.setdefault(
            "RootFolder",
            Folder(self.context, ResourcePath("RootFolder", self.resource_path)),
        )

    @property
    def fields(self) -> FieldCollection:
        """Gets a value that specifies the collection of all fields in the list."""
        return self.properties.setdefault(
            "Fields",
            FieldCollection(self.context, ResourcePath("Fields", self.resource_path), self),
        )

    @property
    def subscriptions(self) -> SubscriptionCollection:
        """Gets one or more webhook subscriptions on a SharePoint list."""
        return self.properties.get(
            "Subscriptions",
            SubscriptionCollection(self.context, ResourcePath("Subscriptions", self.resource_path), self),
        )

    @property
    def views(self) -> ViewCollection:
        """Gets a value that specifies the collection of all public views on the list and personal views
        of the current user on the list."""
        return self.properties.get(
            "Views",
            ViewCollection(self.context, ResourcePath("views", self.resource_path), self),
        )

    @odata(name="DefaultView")
    @property
    def default_view(self) -> View:
        """Gets or sets a value that specifies whether the list view is the default list view."""
        return self.properties.get(
            "DefaultView",
            View(self.context, ResourcePath("DefaultView", self.resource_path), self),
        )

    @odata(name="ContentTypes")
    @property
    def content_types(self) -> ContentTypeCollection:
        """Gets the content types that are associated with the list."""
        return self.properties.get(
            "ContentTypes",
            ContentTypeCollection(self.context, ResourcePath("ContentTypes", self.resource_path), self),
        )

    @property
    def content_types_enabled(self) -> Optional[bool]:
        """Specifies whether content types are enabled for the list."""
        return self.properties.get("ContentTypesEnabled", None)

    @property
    def is_private(self) -> Optional[bool]:
        """
        Specifies whether the list is a private list with restricted permissions.
        True if the list is a private list, otherwise False.
        """
        return self.properties.get("IsPrivate", None)

    @property
    def is_site_assets_library(self) -> Optional[bool]:
        """
        Specifies whether the list is designated as a default asset location for images or other files which the
        users upload to their wiki pages.
        """
        return self.properties.get("IsSiteAssetsLibrary", None)

    @property
    def is_system_list(self) -> Optional[bool]:
        """
        Indicates whether the list is system list that does not contain end user data and created by system account.
        A value of True means yes.
        """
        return self.properties.get("IsSystemList", None)

    @odata(name="UserCustomActions")
    @property
    def user_custom_actions(self) -> UserCustomActionCollection:
        """Gets the User Custom Actions that are associated with the list."""
        return self.properties.get(
            "UserCustomActions",
            UserCustomActionCollection(self.context, ResourcePath("UserCustomActions", self.resource_path)),
        )

    @odata(name="VersionPolicies")
    @property
    def version_policies(self) -> VersionPolicyManager:
        """ """
        return self.properties.get(
            "VersionPolicies",
            VersionPolicyManager(self.context, ResourcePath("VersionPolicies", self.resource_path)),
        )

    @odata(name="CustomActionElements")
    @property
    def custom_action_elements(self) -> CustomActionElementCollection:
        return self.properties.get("CustomActionElements", CustomActionElementCollection())

    @property
    def forms(self) -> FormCollection:
        """Gets a value that specifies the collection of all list forms in the list."""
        return self.properties.get(
            "Forms",
            FormCollection(self.context, ResourcePath("forms", self.resource_path)),
        )

    @odata(name="ParentWeb")
    @property
    def parent_web(self) -> Web:
        """Gets a value that specifies the web where list resides."""
        from office365.sharepoint.webs.web import Web

        return self.properties.get(
            "ParentWeb",
            Web(self.context, ResourcePath("parentWeb", self.resource_path)),
        )

    @odata(name="EventReceivers")
    @property
    def event_receivers(self) -> EventReceiverDefinitionCollection:
        """Get Event receivers"""
        return self.properties.get(
            "EventReceivers",
            EventReceiverDefinitionCollection(self.context, ResourcePath("eventReceivers", self.resource_path), self),
        )

    @property
    def item_count(self) -> Optional[int]:
        """Gets a value that specifies the number of list items in the list"""
        return self.properties.get("ItemCount", None)

    @odata(name="LastItemDeletedDate")
    @property
    def last_item_deleted_date(self) -> Optional[datetime]:
        """
        Specifies the last time a list item was deleted from the list. It MUST return Created if no list item has
        been deleted from the list yet.
        """
        return self.properties.get("LastItemDeletedDate", None)

    @odata(name="LastItemModifiedDate")
    @property
    def last_item_modified_date(self) -> Optional[datetime]:
        """
        Specifies the last time a list item, field, or property of the list was modified.
        It MUST return Created if the list has not been modified.
        """
        return self.properties.get("LastItemModifiedDate", None)

    @odata(name="LastItemUserModifiedDate")
    @property
    def last_item_user_modified_date(self) -> Optional[datetime]:
        """
        Specifies the last time a list item was modified by a user.
        """
        return self.properties.get("LastItemUserModifiedDate", None)

    @property
    def list_experience_options(self) -> Optional[int]:
        """
        Gets or sets the list to new experience, classic experience or default experience set by my administrator.
        """
        return self.properties.get("ListExperienceOptions", None)

    @property
    def list_form_customized(self) -> Optional[bool]:
        """ """
        return self.properties.get("ListFormCustomized", None)

    @property
    def list_item_entity_type_full_name(self) -> Optional[str]:
        """
        Specifies the full type name of the list item.
        """
        return self.properties.get("ListItemEntityTypeFullName", None)

    @property
    def major_version_limit(self) -> Optional[int]:
        """
        Gets the maximum number of major versions allowed for an item in a document library that uses version
        control with major versions only.
        """
        return self.properties.get("MajorVersionLimit", None)

    @property
    def list_schema_version(self) -> Optional[str]:
        """"""
        return self.properties.get("ListSchemaVersion", None)

    @property
    def major_with_minor_versions_limit(self) -> Optional[int]:
        """
        Gets the maximum number of major versions that are allowed for an item in a document library that uses
        version control with both major and minor versions.
        """
        return self.properties.get("MajorWithMinorVersionsLimit", None)

    @property
    def no_crawl(self) -> Optional[bool]:
        """
        Specifies that the crawler MUST NOT crawl the list.
        """
        return self.properties.get("NoCrawl", None)

    @property
    def on_quick_launch(self) -> Optional[bool]:
        """
        Specifies whether the list appears on the Quick Launch of the site (2). If the value is set to "true",
        the protocol server MUST set the Hidden property of the list to "false".
        """
        return self.properties.get("OnQuickLaunch", None)

    @property
    def page_render_type(self) -> Optional[int]:
        """
        Returns the render type of the current file. If the file will render in the modern experience it will return
        ListPageRenderType.Modern. If the file will render in the classic experience, it will return the reason
        for staying in classic, as specified by ListPageRenderType enumeration (section 3.2.5.413).
        """
        return self.properties.get("PageRenderType", None)

    @property
    def parent_web_url(self) -> Optional[str]:
        """
        Specifies the server-relative URL of the site (2) that contains the list.
        It MUST be a URL of server-relative form.
        """
        return self.properties.get("ParentWebUrl", None)

    @property
    def parser_disabled(self) -> Optional[str]:
        """
        Specifies whether or not the document parser is enabled on the list.
        Specify a value of true if the document parser is enabled on the list; specify false if otherwise.
        """
        return self.properties.get("ParserDisabled", None)

    @property
    def read_security(self) -> Optional[int]:
        """Gets or sets the Read security setting for the list."""
        return self.properties.get("ReadSecurity", None)

    @property
    def server_template_can_create_folders(self) -> Optional[bool]:
        """
        Specifies whether the list template the list is based on allows the creation of folders.
        """
        return self.properties.get("ServerTemplateCanCreateFolders", None)

    @property
    def show_hidden_fields_in_modern_form(self) -> Optional[bool]:
        return self.properties.get("ShowHiddenFieldsInModernForm", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the displayed title for the list."""
        return self.properties.get("Title", None)

    @title.setter
    def title(self, val):
        """Sets the displayed title for the list."""
        self.set_property("Title", val)

    @property
    def default_content_approval_workflow_id(self) -> Optional[str]:
        """
        Specifies the default workflow identifier for content approval on the list. It MUST be an empty GUID
        if there is no default content approval workflow
        """
        return self.properties.get("DefaultContentApprovalWorkflowId", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the description for the list."""
        return self.properties.get("Description", None)

    @description.setter
    def description(self, val: str) -> None:
        """Sets the description for the list."""
        self.set_property("Description", val)

    @odata(name="DescriptionResource")
    @property
    def description_resource(self) -> UserResource:
        """Represents the description of this list."""
        return self.properties.get(
            "DescriptionResource",
            UserResource(self.context, ResourcePath("DescriptionResource", self.resource_path)),
        )

    @odata(name="ParentWebPath")
    @property
    def parent_web_path(self) -> SPResPath:
        """Returns the path of the parent web for the list."""
        return self.properties.get("ParentWebPath", SPResPath())

    @property
    def schema_xml(self) -> Optional[str]:
        """Specifies the list schema of the list."""
        return self.properties.get("SchemaXml", None)

    @property
    def template_feature_id(self) -> Optional[str]:
        """
        Specifies the feature identifier of the feature that contains the list schema for the list.
        It MUST be an empty GUID if the list schema for the list is not contained within a feature.
        """
        return self.properties.get("TemplateFeatureId", None)

    @odata(name="TitleResource")
    @property
    def title_resource(self) -> UserResource:
        """Represents the title of this list."""
        return self.properties.get(
            "TitleResource",
            UserResource(self.context, ResourcePath("TitleResource", self.resource_path)),
        )

    @property
    def validation_formula(self) -> Optional[str]:
        """Specifies the data validation criteria for a list item."""
        return self.properties.get("ValidationFormula", None)

    def set_property(self, name, value, persist_changes=True):
        super().set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Url":
                self._resource_path = ServiceOperationPath("getList", [value], self.context.web.resource_path)
        return self

    @property
    def color(self) -> Optional[str]:
        """Gets the Color property"""
        return self.properties.get("Color", None)

    @property
    def default_new_form_url(self) -> Optional[str]:
        """Gets the DefaultNewFormUrl property"""
        return self.properties.get("DefaultNewFormUrl", None)

    @property
    def direction(self) -> Optional[str]:
        """Gets the Direction property"""
        return self.properties.get("Direction", None)

    @property
    def document_read_security(self) -> Optional[bool]:
        """Gets the DocumentReadSecurity property"""
        return self.properties.get("DocumentReadSecurity", None)

    @property
    def draft_version_visibility(self) -> Optional[int]:
        """Gets the DraftVersionVisibility property"""
        return self.properties.get("DraftVersionVisibility", None)

    @property
    def enabled_queryable_columns_datetime(self) -> Optional[datetime]:
        """Gets the EnabledQueryableColumnsDateTime property"""
        return self.properties.get("EnabledQueryableColumnsDateTime", datetime.min)

    @property
    def exclude_from_offline_mode(self) -> Optional[bool]:
        """Gets the ExcludeFromOfflineMode property"""
        return self.properties.get("ExcludeFromOfflineMode", None)

    @property
    def extended_sharepoint_permission_offline_days_for_library(self) -> Optional[int]:
        """Gets the ExtendedSharePointPermissionOfflineDaysForLibrary property"""
        return self.properties.get("ExtendedSharePointPermissionOfflineDaysForLibrary", None)

    @property
    def has_copy_move_rules(self) -> Optional[bool]:
        """Gets the HasCopyMoveRules property"""
        return self.properties.get("HasCopyMoveRules", None)

    @property
    def has_list_bound_content_assembly_templates(self) -> Optional[bool]:
        """Gets the HasListBoundContentAssemblyTemplates property"""
        return self.properties.get("HasListBoundContentAssemblyTemplates", None)

    @property
    def high_priority_media_processing(self) -> Optional[bool]:
        """Gets the HighPriorityMediaProcessing property"""
        return self.properties.get("HighPriorityMediaProcessing", None)

    @property
    def icon(self) -> Optional[str]:
        """Gets the Icon property"""
        return self.properties.get("Icon", None)

    @property
    def image_path(self) -> ResourcePath:
        """Gets the ImagePath property"""
        from office365.sharepoint.types.resource_path import ResourcePath

        return self.properties.get("ImagePath", ResourcePath())

    @property
    def image_url(self) -> Optional[str]:
        """Gets the ImageUrl property"""
        return self.properties.get("ImageUrl", None)

    @property
    def default_sensitivity_label_for_library(self) -> Optional[str]:
        """Gets the DefaultSensitivityLabelForLibrary property"""
        return self.properties.get("DefaultSensitivityLabelForLibrary", None)

    @property
    def sensitivity_label_to_encrypt_on_download_for_library(self) -> Optional[str]:
        """Gets the SensitivityLabelToEncryptOnDownloadForLibrary property"""
        return self.properties.get("SensitivityLabelToEncryptOnDownloadForLibrary", None)

    @property
    def irm_reject(self) -> Optional[bool]:
        """Gets the IrmReject property"""
        return self.properties.get("IrmReject", None)

    @property
    def is_application_list(self) -> Optional[bool]:
        """Gets the IsApplicationList property"""
        return self.properties.get("IsApplicationList", None)

    @property
    def is_catalog(self) -> Optional[bool]:
        """Gets the IsCatalog property"""
        return self.properties.get("IsCatalog", None)

    @property
    def is_contributor_owner_enabled(self) -> Optional[bool]:
        """Gets the IsContributorOwnerEnabled property"""
        return self.properties.get("IsContributorOwnerEnabled", None)

    @property
    def is_default_document_library(self) -> Optional[bool]:
        """Gets the IsDefaultDocumentLibrary property"""
        return self.properties.get("IsDefaultDocumentLibrary", None)

    @property
    def is_enterprise_gallery_library(self) -> Optional[bool]:
        """Gets the IsEnterpriseGalleryLibrary property"""
        return self.properties.get("IsEnterpriseGalleryLibrary", None)

    @property
    def is_prediction_model_applied(self) -> Optional[bool]:
        """Gets the IsPredictionModelApplied property"""
        return self.properties.get("IsPredictionModelApplied", None)

    @property
    def multiple_data_list(self) -> Optional[bool]:
        """Gets the MultipleDataList property"""
        return self.properties.get("MultipleDataList", None)

    @property
    def show_one_tab_only(self) -> Optional[bool]:
        """Gets the ShowOneTabOnly property"""
        return self.properties.get("ShowOneTabOnly", None)

    @property
    def template_type_id(self) -> Optional[str]:
        """Gets the TemplateTypeId property"""
        return self.properties.get("TemplateTypeId", None)

    @property
    def validation_message(self) -> Optional[str]:
        """Gets the ValidationMessage property"""
        return self.properties.get("ValidationMessage", None)

    @property
    def write_security(self) -> Optional[int]:
        """Gets the WriteSecurity property"""
        return self.properties.get("WriteSecurity", None)

    @property
    def extended_sharepoint_permission_settings(self) -> ExtendedSharePointPermissionSettings:
        """Gets the ExtendedSharePointPermissionSettings property"""
        from office365.sharepoint.lists.extended_share_point_permission_settings import (
            ExtendedSharePointPermissionSettings,
        )

        return self.properties.get(
            "ExtendedSharePointPermissionSettings",
            ExtendedSharePointPermissionSettings(
                self.context, ResourcePath("ExtendedSharePointPermissionSettings", self.resource_path)
            ),
        )

    @property
    def information_rights_management_settings(self) -> InformationRightsManagementSettings:
        """Gets the InformationRightsManagementSettings property"""
        from office365.sharepoint.permissions.irm.settings import (
            InformationRightsManagementSettings,
        )

        return self.properties.get(
            "InformationRightsManagementSettings",
            InformationRightsManagementSettings(
                self.context, ResourcePath("InformationRightsManagementSettings", self.resource_path)
            ),
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

    def add_validate_update_item_using_path(
        self,
        list_item_create_info: ListItemCreationInformationUsingPath,
        form_values: ClientValueCollection[ListItemFormUpdateValue],
        bnew_document_update: bool,
        check_in_comment: str,
        dates_in_utc: bool,
        number_in_invariant_culture: bool,
    ) -> ClientResult[ClientValueCollection[ListItemFormUpdateValue]]:
        """AddValidateUpdateItemUsingPath operation.

        Args:
            list_item_create_info (ListItemCreationInformationUsingPath):
                listItemCreateInfo parameter
            form_values (ClientValueCollection[ListItemFormUpdateValue]):
                formValues parameter
            bnew_document_update (bool):
                bNewDocumentUpdate parameter
            check_in_comment (str):
                checkInComment parameter
            dates_in_utc (bool):
                datesInUTC parameter
            number_in_invariant_culture (bool):
                numberInInvariantCulture parameter
        """
        from office365.sharepoint.listitems.form_update_value import (
            ListItemFormUpdateValue,
        )

        return_type = ClientResult(self.context, ClientValueCollection[ListItemFormUpdateValue]())
        qry = ServiceOperationQuery(
            self,
            "AddValidateUpdateItemUsingPath",
            None,
            {
                "listItemCreateInfo": list_item_create_info,
                "formValues": form_values,
                "bNewDocumentUpdate": bnew_document_update,
                "checkInComment": check_in_comment,
                "datesInUTC": dates_in_utc,
                "numberInInvariantCulture": number_in_invariant_culture,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def caae_create_temp_folder(self) -> ClientResult[str]:
        """CAAECreateTempFolder operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "CAAECreateTempFolder", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def caae_rename_file_in_temporary_folder(self, path: str, updated_name: str) -> ClientResult[str]:
        """CAAERenameFileInTemporaryFolder operation.

        Args:
            path (str):
                Path parameter
            updated_name (str):
                UpdatedName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "CAAERenameFileInTemporaryFolder", None, {"Path": path, "UpdatedName": updated_name}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def cancel_delete_file_versions(self) -> Self:
        """CancelDeleteFileVersions operation."""
        qry = ServiceOperationQuery(self, "CancelDeleteFileVersions", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def clear_business_app_migration_interactive_data(self) -> Self:
        """ClearBusinessAppMigrationInteractiveData operation."""
        qry = ServiceOperationQuery(self, "ClearBusinessAppMigrationInteractiveData", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def copy_template_and_get_metadata(self, id_: str) -> ClientResult[TemplatizationMetaData]:
        """CopyTemplateAndGetMetadata operation.

        Args:
            id_ (str):
                Id parameter
        """
        from office365.sharepoint.lists.templatization_metadata import (
            TemplatizationMetaData,
        )

        return_type = ClientResult(self.context, TemplatizationMetaData())
        qry = ServiceOperationQuery(self, "CopyTemplateAndGetMetadata", None, {"Id": id_}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_document_from_caae_template(
        self, content_type_name: str, document_generation_info: DocumentGenerationInfo
    ) -> ClientResult[ContentAssemblyFileInfo]:
        """CreateDocumentFromCAAETemplate operation.

        Args:
            content_type_name (str):
                ContentTypeName parameter
            document_generation_info (DocumentGenerationInfo):
                documentGenerationInfo parameter
        """
        from office365.sharepoint.documents.contentassemblyfileinfo import (
            ContentAssemblyFileInfo,
        )

        return_type = ClientResult(self.context, ContentAssemblyFileInfo())
        qry = ServiceOperationQuery(
            self,
            "CreateDocumentFromCAAETemplate",
            None,
            {"ContentTypeName": content_type_name, "documentGenerationInfo": document_generation_info},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def create_document_from_caae_template_v2(
        self, id_: str, document_generation_info: DocumentGenerationInfo
    ) -> ClientResult[ContentAssemblyFileInfo]:
        """CreateDocumentFromCAAETemplateV2 operation.

        Args:
            id_ (str):
                Id parameter
            document_generation_info (DocumentGenerationInfo):
                documentGenerationInfo parameter
        """
        from office365.sharepoint.documents.contentassemblyfileinfo import (
            ContentAssemblyFileInfo,
        )

        return_type = ClientResult(self.context, ContentAssemblyFileInfo())
        qry = ServiceOperationQuery(
            self,
            "CreateDocumentFromCAAETemplateV2",
            None,
            {"Id": id_, "documentGenerationInfo": document_generation_info},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def create_document_from_content_assembly_template(
        self, template_url: str, document_generation_info: DocumentGenerationInfo
    ) -> ClientResult[ContentAssemblyFileInfo]:
        """CreateDocumentFromContentAssemblyTemplate operation.

        Args:
            template_url (str):
                TemplateUrl parameter
            document_generation_info (DocumentGenerationInfo):
                documentGenerationInfo parameter
        """
        from office365.sharepoint.documents.contentassemblyfileinfo import (
            ContentAssemblyFileInfo,
        )

        return_type = ClientResult(self.context, ContentAssemblyFileInfo())
        qry = ServiceOperationQuery(
            self,
            "CreateDocumentFromContentAssemblyTemplate",
            None,
            {"TemplateUrl": template_url, "documentGenerationInfo": document_generation_info},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def create_hvcs_item_approval_request(
        self, create_item_request_payload: CreateHVCSItemApprovalRequestParameters
    ) -> ClientResult[str]:
        """CreateHVCSItemApprovalRequest operation.

        Args:
            create_item_request_payload (CreateHVCSItemApprovalRequestParameters):
                createItemRequestPayload parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "CreateHVCSItemApprovalRequest",
            None,
            {"createItemRequestPayload": create_item_request_payload},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def create_list_form(self, parameters: ListForm) -> ClientResult[ListForm]:
        """CreateListForm operation.

        Args:
            parameters (ListForm):
                parameters parameter
        """
        from office365.sharepoint.lists.listform import ListForm

        return_type = ClientResult(self.context, ListForm())
        qry = ServiceOperationQuery(self, "CreateListForm", None, {"parameters": parameters}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_rule_ex(
        self, condition: str, title: str, trigger_type: int, action: SPRuleAction, rule_template_id: str
    ) -> ClientResult[UUID]:
        """CreateRuleEx operation.

        Args:
            condition (str):
                condition parameter
            title (str):
                title parameter
            trigger_type (int):
                triggerType parameter
            action (SPRuleAction):
                action parameter
            rule_template_id (str):
                ruleTemplateId parameter
        """
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(
            self,
            "CreateRuleEx",
            None,
            {
                "condition": condition,
                "title": title,
                "triggerType": trigger_type,
                "action": action,
                "ruleTemplateId": rule_template_id,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def enable_queryable_columns(self) -> Self:
        """EnableQueryableColumns operation."""
        qry = ServiceOperationQuery(self, "EnableQueryableColumns", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def get_async_action_task_ids(self) -> ClientResult[GuidCollection]:
        """GetAsyncActionTaskIds operation."""
        return_type = ClientResult(self.context, GuidCollection())
        qry = ServiceOperationQuery(self, "GetAsyncActionTaskIds", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_business_app_migration_interactive_data(self) -> ClientResult[str]:
        """GetBusinessAppMigrationInteractiveData operation."""
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetBusinessAppMigrationInteractiveData", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_caae_template_metadata(self, name: str, published: bool) -> ClientResult[TemplateMetaData]:
        """GetCAAETemplateMetadata operation.

        Args:
            name (str):
                Name parameter
            published (bool):
                Published parameter
        """
        from office365.sharepoint.documents.templatemetadata import TemplateMetaData

        return_type = ClientResult(self.context, TemplateMetaData())
        qry = FunctionQuery(self, "GetCAAETemplateMetadata", [name, published], return_type)
        self.context.add_query(qry)
        return return_type

    def get_caae_template_metadata_v2(self, id_: str) -> ClientResult[ClientValueCollection[PlaceholderV2]]:
        """GetCAAETemplateMetadataV2 operation.

        Args:
            id_ (str):
                Id parameter
        """
        from office365.sharepoint.documents.placeholderv2 import PlaceholderV2

        return_type = ClientResult(self.context, ClientValueCollection[PlaceholderV2]())
        qry = FunctionQuery(self, "GetCAAETemplateMetadataV2", [id_], return_type)
        self.context.add_query(qry)
        return return_type

    def get_content_assembly_document_field_values(self, document_url: str) -> ClientResult[FieldValuesWithUrl]:
        """GetContentAssemblyDocumentFieldValues operation.

        Args:
            document_url (str):
                DocumentUrl parameter
        """
        from office365.sharepoint.documents.fieldvalueswithurl import FieldValuesWithUrl

        return_type = ClientResult(self.context, FieldValuesWithUrl())
        qry = FunctionQuery(self, "GetContentAssemblyDocumentFieldValues", [document_url], return_type)
        self.context.add_query(qry)
        return return_type

    def get_content_assembly_template_fields(
        self, template_url: str
    ) -> ClientResult[ClientValueCollection[PlaceholderV2]]:
        """GetContentAssemblyTemplateFields operation.

        Args:
            template_url (str):
                TemplateUrl parameter
        """
        from office365.sharepoint.documents.placeholderv2 import PlaceholderV2

        return_type = ClientResult(self.context, ClientValueCollection[PlaceholderV2]())
        qry = FunctionQuery(self, "GetContentAssemblyTemplateFields", [template_url], return_type)
        self.context.add_query(qry)
        return return_type

    def get_list_forms(self, bsanitize: bool) -> ClientResult[ClientValueCollection[ListForm]]:
        """GetListForms operation.

        Args:
            bsanitize (bool):
                bSanitize parameter
        """
        from office365.sharepoint.lists.listform import ListForm

        return_type = ClientResult(self.context, ClientValueCollection[ListForm]())
        qry = FunctionQuery(self, "GetListForms", [bsanitize], return_type)
        self.context.add_query(qry)
        return return_type

    def get_progress_for_delete_file_versions(self) -> ClientResult[str]:
        """GetProgressForDeleteFileVersions operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetProgressForDeleteFileVersions", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_progress_for_file_version_expiration_report(self, report_file_url: str) -> ClientResult[str]:
        """GetProgressForFileVersionExpirationReport operation.

        Args:
            report_file_url (str):
                reportFileUrl parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "GetProgressForFileVersionExpirationReport",
            None,
            {"reportFileUrl": report_file_url},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def is_syntex_ai_features_flight_enabled(self) -> ClientResult[bool]:
        """IsSyntexAIFeaturesFlightEnabled operation."""
        return_type = ClientResult(self.context, bool())
        qry = FunctionQuery(self, "IsSyntexAIFeaturesFlightEnabled", [], return_type)
        self.context.add_query(qry)
        return return_type

    def lock_smart_template(self, id_: str) -> ClientResult[LockFileData]:
        """LockSmartTemplate operation.

        Args:
            id_ (str):
                Id parameter
        """
        from office365.sharepoint.documents.lockfiledata import LockFileData

        return_type = ClientResult(self.context, LockFileData())
        qry = ServiceOperationQuery(self, "LockSmartTemplate", None, {"Id": id_}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def map_fields_to_columns_for_modern_temlate(
        self, payload: PublishModernTemplatePayload
    ) -> ClientResult[ContentAssemblyModernTemplateColumnsMappingInfo]:
        """MapFieldsToColumnsForModernTemlate operation.

        Args:
            payload (PublishModernTemplatePayload):
                payload parameter
        """
        from office365.sharepoint.documents.contentassemblymoderntemplatecolumnsmappinginfo import (
            ContentAssemblyModernTemplateColumnsMappingInfo,
        )

        return_type = ClientResult(self.context, ContentAssemblyModernTemplateColumnsMappingInfo())
        qry = ServiceOperationQuery(
            self, "MapFieldsToColumnsForModernTemlate", None, {"payload": payload}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def map_fields_to_columns_for_modern_template(
        self, template_payload: PublishModernTemplatePayload
    ) -> ClientResult[ContentAssemblyModernTemplateColumnsMappingInfo]:
        """MapFieldsToColumnsForModernTemplate operation.

        Args:
            template_payload (PublishModernTemplatePayload):
                templatePayload parameter
        """
        from office365.sharepoint.documents.contentassemblymoderntemplatecolumnsmappinginfo import (
            ContentAssemblyModernTemplateColumnsMappingInfo,
        )

        return_type = ClientResult(self.context, ContentAssemblyModernTemplateColumnsMappingInfo())
        qry = ServiceOperationQuery(
            self, "MapFieldsToColumnsForModernTemplate", None, {"templatePayload": template_payload}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def parse_document_template(self, name: str) -> ClientResult[str]:
        """ParseDocumentTemplate operation.

        Args:
            name (str):
                Name parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "ParseDocumentTemplate", None, {"Name": name}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def publish_snippet(self, publish_snippet_payload: PublishSnippetPayload) -> Self:
        """PublishSnippet operation.

        Args:
            publish_snippet_payload (PublishSnippetPayload):
                publishSnippetPayload parameter
        """
        qry = ServiceOperationQuery(
            self, "PublishSnippet", None, {"publishSnippetPayload": publish_snippet_payload}, None, None
        )
        self.context.add_query(qry)
        return self

    def publish_template_v2(self, payload: PublishTemplateV2Payload) -> Self:
        """PublishTemplateV2 operation.

        Args:
            payload (PublishTemplateV2Payload):
                payload parameter
        """
        qry = ServiceOperationQuery(self, "PublishTemplateV2", None, {"payload": payload}, None, None)
        self.context.add_query(qry)
        return self

    def refresh_lock_smart_template(self, id_: str, lock_id: str) -> ClientResult[LockFileData]:
        """RefreshLockSmartTemplate operation.

        Args:
            id_ (str):
                Id parameter
            lock_id (str):
                LockId parameter
        """
        from office365.sharepoint.documents.lockfiledata import LockFileData

        return_type = ClientResult(self.context, LockFileData())
        qry = ServiceOperationQuery(
            self, "RefreshLockSmartTemplate", None, {"Id": id_, "LockId": lock_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def render_extended_list_form_data(
        self, item_id: int, form_id: str, mode: int, options: int, cutoff_version: int
    ) -> ClientResult[str]:
        """RenderExtendedListFormData operation.

        Args:
            item_id (int):
                itemId parameter
            form_id (str):
                formId parameter
            mode (int):
                mode parameter
            options (int):
                options parameter
            cutoff_version (int):
                cutoffVersion parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "RenderExtendedListFormData",
            None,
            {"itemId": item_id, "formId": form_id, "mode": mode, "options": options, "cutoffVersion": cutoff_version},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def render_list_context_menu_data(
        self,
        casc_del_warn_message: str,
        custom_action: str,
        field: str,
        id_: str,
        inplace_full_list_search: str,
        inplace_search_query: str,
        is_csr: str,
        is_xsl_view: str,
        item_id: str,
        list_view_page_url: str,
        override_scope: str,
        root_folder: str,
        view: str,
        view_count: str,
    ) -> ClientResult[bytes]:
        """RenderListContextMenuData operation.

        Args:
            casc_del_warn_message (str):
                CascDelWarnMessage parameter
            custom_action (str):
                CustomAction parameter
            field (str):
                Field parameter
            id_ (str):
                ID parameter
            inplace_full_list_search (str):
                InplaceFullListSearch parameter
            inplace_search_query (str):
                InplaceSearchQuery parameter
            is_csr (str):
                IsCSR parameter
            is_xsl_view (str):
                IsXslView parameter
            item_id (str):
                ItemId parameter
            list_view_page_url (str):
                ListViewPageUrl parameter
            override_scope (str):
                OverrideScope parameter
            root_folder (str):
                RootFolder parameter
            view (str):
                View parameter
            view_count (str):
                ViewCount parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self,
            "RenderListContextMenuData",
            None,
            {
                "CascDelWarnMessage": casc_del_warn_message,
                "CustomAction": custom_action,
                "Field": field,
                "ID": id_,
                "InplaceFullListSearch": inplace_full_list_search,
                "InplaceSearchQuery": inplace_search_query,
                "IsCSR": is_csr,
                "IsXslView": is_xsl_view,
                "ItemId": item_id,
                "ListViewPageUrl": list_view_page_url,
                "OverrideScope": override_scope,
                "RootFolder": root_folder,
                "View": view,
                "ViewCount": view_count,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def render_list_filter_data(
        self,
        exclude_field_filtering_html: bool,
        field_internal_name: str,
        override_scope: str,
        process_q_string_to_caml: str,
        view_id: str,
        view_xml: str,
    ) -> ClientResult[bytes]:
        """RenderListFilterData operation.

        Args:
            exclude_field_filtering_html (bool):
                ExcludeFieldFilteringHtml parameter
            field_internal_name (str):
                FieldInternalName parameter
            override_scope (str):
                OverrideScope parameter
            process_q_string_to_caml (str):
                ProcessQStringToCAML parameter
            view_id (str):
                ViewId parameter
            view_xml (str):
                ViewXml parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self,
            "RenderListFilterData",
            None,
            {
                "ExcludeFieldFilteringHtml": exclude_field_filtering_html,
                "FieldInternalName": field_internal_name,
                "OverrideScope": override_scope,
                "ProcessQStringToCAML": process_q_string_to_caml,
                "ViewId": view_id,
                "ViewXml": view_xml,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def render_list_form_data(self, item_id: int, form_id: str, mode: int) -> ClientResult[str]:
        """RenderListFormData operation.

        Args:
            item_id (int):
                itemId parameter
            form_id (str):
                formId parameter
            mode (int):
                mode parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "RenderListFormData", None, {"itemId": item_id, "formId": form_id, "mode": mode}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def set_column_mapping(self, column_mapping: str) -> Self:
        """SetColumnMapping operation.

        Args:
            column_mapping (str):
                columnMapping parameter
        """
        qry = ServiceOperationQuery(self, "SetColumnMapping", None, {"columnMapping": column_mapping}, None, None)
        self.context.add_query(qry)
        return self

    def set_content_assembly_template_read_only(self, id_: str) -> Self:
        """SetContentAssemblyTemplateReadOnly operation.

        Args:
            id_ (str):
                Id parameter
        """
        qry = ServiceOperationQuery(self, "SetContentAssemblyTemplateReadOnly", None, {"Id": id_}, None, None)
        self.context.add_query(qry)
        return self

    def set_items_order(
        self, item_ids: list[int], lower_order_item_id: int, higher_order_item_id: int, use_provided_order_item_id: bool
    ) -> ClientResult[ClientValueCollection[ItemOrderUpdateValue]]:
        """SetItemsOrder operation.

        Args:
            item_ids (list[int]):
                itemIds parameter
            lower_order_item_id (int):
                lowerOrderItemId parameter
            higher_order_item_id (int):
                higherOrderItemId parameter
            use_provided_order_item_id (bool):
                useProvidedOrderItemId parameter
        """
        from office365.sharepoint.documents.itemorderupdatevalue import (
            ItemOrderUpdateValue,
        )

        return_type = ClientResult(self.context, ClientValueCollection[ItemOrderUpdateValue]())
        qry = ServiceOperationQuery(
            self,
            "SetItemsOrder",
            None,
            {
                "itemIds": ClientValueCollection(int, item_ids),
                "lowerOrderItemId": lower_order_item_id,
                "higherOrderItemId": higher_order_item_id,
                "useProvidedOrderItemId": use_provided_order_item_id,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_list_custom_order_flag(self, value: bool) -> Self:
        """SetListCustomOrderFlag operation.

        Args:
            value (bool):
                value parameter
        """
        qry = ServiceOperationQuery(self, "SetListCustomOrderFlag", None, {"value": value}, None, None)
        self.context.add_query(qry)
        return self

    def set_quickstep_ordering(self, quickstep_ids: str) -> Self:
        """SetQuickstepOrdering operation.

        Args:
            quickstep_ids (str):
                quickstepIds parameter
        """
        qry = ServiceOperationQuery(self, "SetQuickstepOrdering", None, {"quickstepIds": quickstep_ids}, None, None)
        self.context.add_query(qry)
        return self

    def start_delete_file_versions(self, delete_older_than_days: int) -> Self:
        """StartDeleteFileVersions operation.

        Args:
            delete_older_than_days (int):
                deleteOlderThanDays parameter
        """
        qry = ServiceOperationQuery(
            self, "StartDeleteFileVersions", None, {"deleteOlderThanDays": delete_older_than_days}, None, None
        )
        self.context.add_query(qry)
        return self

    def start_delete_file_versions_by_mode(self, batch_delete_parameters: FileVersionBatchDeleteParameters) -> Self:
        """StartDeleteFileVersionsByMode operation.

        Args:
            batch_delete_parameters (FileVersionBatchDeleteParameters):
                batchDeleteParameters parameter
        """
        qry = ServiceOperationQuery(
            self, "StartDeleteFileVersionsByMode", None, {"batchDeleteParameters": batch_delete_parameters}, None, None
        )
        self.context.add_query(qry)
        return self

    def start_file_version_expiration_report(self, report_file_url: str) -> Self:
        """StartFileVersionExpirationReport operation.

        Args:
            report_file_url (str):
                reportFileUrl parameter
        """
        qry = ServiceOperationQuery(
            self, "StartFileVersionExpirationReport", None, {"reportFileUrl": report_file_url}, None, None
        )
        self.context.add_query(qry)
        return self

    def unlock_smart_template(self, id_: str, lock_id: str) -> Self:
        """UnlockSmartTemplate operation.

        Args:
            id_ (str):
                Id parameter
            lock_id (str):
                LockId parameter
        """
        qry = ServiceOperationQuery(self, "UnlockSmartTemplate", None, {"Id": id_, "LockId": lock_id}, None, None)
        self.context.add_query(qry)
        return self

    def unset_content_assembly_template_read_only(self, id_: str) -> Self:
        """UnsetContentAssemblyTemplateReadOnly operation.

        Args:
            id_ (str):
                Id parameter
        """
        qry = ServiceOperationQuery(self, "UnsetContentAssemblyTemplateReadOnly", None, {"Id": id_}, None, None)
        self.context.add_query(qry)
        return self

    def update_caae_template(self, name: str, update_template_info: UpdateTemplateInfo) -> Self:
        """UpdateCAAETemplate operation.

        Args:
            name (str):
                Name parameter
            update_template_info (UpdateTemplateInfo):
                updateTemplateInfo parameter
        """
        qry = ServiceOperationQuery(
            self, "UpdateCAAETemplate", None, {"Name": name, "updateTemplateInfo": update_template_info}, None, None
        )
        self.context.add_query(qry)
        return self

    def update_caae_template_v2(self, id_: str, update_template_info: UpdateTemplateInfoV2) -> Self:
        """UpdateCAAETemplateV2 operation.

        Args:
            id_ (str):
                Id parameter
            update_template_info (UpdateTemplateInfoV2):
                updateTemplateInfo parameter
        """
        qry = ServiceOperationQuery(
            self, "UpdateCAAETemplateV2", None, {"Id": id_, "updateTemplateInfo": update_template_info}, None, None
        )
        self.context.add_query(qry)
        return self

    def update_content_assembly_document(
        self, template_url: str, content_assembly_form_answers: ClientValueCollection[ContentAssemblyFormAnswer]
    ) -> ClientResult[ContentAssemblyFileInfo]:
        """UpdateContentAssemblyDocument operation.

        Args:
            template_url (str):
                TemplateUrl parameter
            content_assembly_form_answers (ClientValueCollection[ContentAssemblyFormAnswer]):
                contentAssemblyFormAnswers parameter
        """
        from office365.sharepoint.documents.contentassemblyfileinfo import (
            ContentAssemblyFileInfo,
        )

        return_type = ClientResult(self.context, ContentAssemblyFileInfo())
        qry = ServiceOperationQuery(
            self,
            "UpdateContentAssemblyDocument",
            None,
            {"TemplateUrl": template_url, "contentAssemblyFormAnswers": content_assembly_form_answers},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def update_form_processing_model_retention_label(self, retention_label: str) -> Self:
        """UpdateFormProcessingModelRetentionLabel operation.

        Args:
            retention_label (str):
                retentionLabel parameter
        """
        qry = ServiceOperationQuery(
            self, "UpdateFormProcessingModelRetentionLabel", None, {"retentionLabel": retention_label}, None, None
        )
        self.context.add_query(qry)
        return self

    def update_form_processing_model_settings(self, retention_label: str, linked_list: str) -> Self:
        """UpdateFormProcessingModelSettings operation.

        Args:
            retention_label (str):
                retentionLabel parameter
            linked_list (str):
                linkedList parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UpdateFormProcessingModelSettings",
            None,
            {"retentionLabel": retention_label, "linkedList": linked_list},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def update_list_form(self, parameters: ListForm) -> ClientResult[ListForm]:
        """UpdateListForm operation.

        Args:
            parameters (ListForm):
                parameters parameter
        """
        from office365.sharepoint.lists.listform import ListForm

        return_type = ClientResult(self.context, ListForm())
        qry = ServiceOperationQuery(self, "UpdateListForm", None, {"parameters": parameters}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def update_rule_ex(
        self, rule_id: str, condition: str, title: str, status: int, action: SPRuleAction, trigger_type: int
    ) -> Self:
        """UpdateRuleEx operation.

        Args:
            rule_id (str):
                ruleId parameter
            condition (str):
                condition parameter
            title (str):
                title parameter
            status (int):
                status parameter
            action (SPRuleAction):
                action parameter
            trigger_type (int):
                triggerType parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UpdateRuleEx",
            None,
            {
                "ruleId": rule_id,
                "condition": condition,
                "title": title,
                "status": status,
                "action": action,
                "triggerType": trigger_type,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self
