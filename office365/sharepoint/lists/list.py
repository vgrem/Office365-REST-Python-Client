from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.changes.collection import ChangeCollection
from office365.sharepoint.changes.query import ChangeQuery
from office365.sharepoint.changes.token import ChangeToken
from office365.sharepoint.contenttypes.collection import ContentTypeCollection
from office365.sharepoint.customactions.element_collection import CustomActionElementCollection
from office365.sharepoint.eventreceivers.definition_collection import EventReceiverDefinitionCollection
from office365.sharepoint.fields.collection import FieldCollection
from office365.sharepoint.fields.related_field_collection import RelatedFieldCollection
from office365.sharepoint.files.checked_out_file_collection import CheckedOutFileCollection
from office365.sharepoint.files.file import File
from office365.sharepoint.flows.synchronization_result import FlowSynchronizationResult
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.forms.collection import FormCollection
from office365.sharepoint.listitems.caml.query import CamlQuery
from office365.sharepoint.listitems.creation_information_using_path import ListItemCreationInformationUsingPath
from office365.sharepoint.listitems.form_update_value import ListItemFormUpdateValue
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.listitems.collection import ListItemCollection
from office365.sharepoint.lists.bloom_filter import ListBloomFilter
from office365.sharepoint.lists.creatables_info import CreatablesInfo
from office365.sharepoint.lists.data_source import ListDataSource
from office365.sharepoint.lists.rule import SPListRule
from office365.sharepoint.pages.wiki_page_creation_information import WikiPageCreationInformation
from office365.sharepoint.permissions.securable_object import SecurableObject
from office365.sharepoint.principal.users.user import User
from office365.sharepoint.sitescripts.utility import SiteScriptUtility
from office365.sharepoint.translation.user_resource import UserResource
from office365.sharepoint.usercustomactions.collection import UserCustomActionCollection
from office365.sharepoint.views.view import View
from office365.sharepoint.views.collection import ViewCollection
from office365.sharepoint.webhooks.subscription_collection import SubscriptionCollection
from office365.sharepoint.utilities.utility import Utility
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath


class List(SecurableObject):
    """
    Represents a list on a SharePoint Web site.

    A container within a SharePoint site that stores list items. A list has a customizable schema that is
    composed of one or more fields.
    """

    def __init__(self, context, resource_path=None):
        super(List, self).__init__(context, resource_path)

    def create_document_and_get_edit_link(self, file_name=None, folder_path=None,
                                          document_template_type=1, template_url=None):
        """
        Creates a document at the path and of the type specified within the current list.
        Returns an edit link to the file.

        :param str file_name: Specifies the name of the document.
        :param str folder_path: Specifies the path within the current list to create the document in.
        :param str document_template_type: A number representing the type of document to create.
        :param str template_url: Specifies the URL of the document template (2) to base the new document on.
        """
        return_type = ClientResult(self.context, str())
        payload = {
            "fileName": file_name,
            "folderPath": folder_path,
            "documentTemplateType": document_template_type,
            "templateUrl": template_url
        }
        qry = ServiceOperationQuery(self, "CreateDocumentAndGetEditLink", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def delete_rule(self, rule_id):
        """
        :param str rule_id:
        """
        payload = {"ruleId": rule_id}
        qry = ServiceOperationQuery(self, "DeleteRule", None, payload)
        self.context.add_query(qry)
        return self

    def get_bloom_filter(self, start_item_id=None):
        """
        Generates a Bloom filter (probabilistic structure for checking the existence of list items) for the current list

        :param int start_item_id: he ID of the list item to start the search at.
        """
        return_type = ListBloomFilter(self.context)
        payload = {"startItemId": start_item_id}
        qry = ServiceOperationQuery(self, "GetBloomFilter", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_script(self, options=None):
        """Creates site script syntax

        :param dict or None options:
        """
        return_type = ClientResult(self.context)

        def _list_loaded():
            list_abs_path = SPResPath.create_absolute(self.context.base_url, self.root_folder.serverRelativeUrl)
            SiteScriptUtility.get_site_script_from_list(self.context, str(list_abs_path), options, return_type=return_type)
        self.ensure_property("RootFolder", _list_loaded)
        return return_type

    def get_all_rules(self):
        """
        Retrieves rules of a List
        """
        return_type = ClientResult(self.context, ClientValueCollection(SPListRule))
        qry = ServiceOperationQuery(self, "GetAllRules", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_business_app_operation_status(self):
        """

        """
        return_type = FlowSynchronizationResult(self.context)
        qry = ServiceOperationQuery(self, "GetBusinessAppOperationStatus", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def search_lookup_field_choices(self, target_field_name, begins_with_search_string, paging_info):
        """
        :param str target_field_name:
        :param str begins_with_search_string:
        :param str paging_info:
        """
        return_type = FlowSynchronizationResult(self.context)
        payload = {
            "targetFieldName": target_field_name,
            "beginsWithSearchString": begins_with_search_string,
            "pagingInfo": paging_info
        }
        qry = ServiceOperationQuery(self, "SearchLookupFieldChoices", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def sync_flow_callback_url(self, flow_id):
        """
        :param str flow_id:
        """
        return_type = FlowSynchronizationResult(self.context)
        qry = ServiceOperationQuery(self, "SyncFlowCallbackUrl", None, {"flowId": flow_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def sync_flow_instance(self, flow_id):
        """
        :param str flow_id:
        """
        return_type = FlowSynchronizationResult(self.context)
        qry = ServiceOperationQuery(self, "SyncFlowInstance", None, {"flowId": flow_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def sync_flow_instances(self, retrieve_group_flows):
        """
        :param bool retrieve_group_flows:
        """
        return_type = FlowSynchronizationResult(self.context)
        payload = {"retrieveGroupFlows": retrieve_group_flows}
        qry = ServiceOperationQuery(self, "SyncFlowInstances", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def sync_flow_templates(self, category):
        """
        :param str category:
        """
        return_type = FlowSynchronizationResult(self.context)
        payload = {"category": category}
        qry = ServiceOperationQuery(self, "SyncFlowTemplates", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_document_with_default_name(self, folder_path, extension):
        """
        Creates a empty document with default filename with the given extension at the path given by folderPath.
        Returns the name of the newly created document.

        :param str folder_path: The path within the current list at which to create the document.
        :param str extension: The file extension without dot prefix.
        """
        return_type = ClientResult(self.context)
        payload = {
            "folderPath": folder_path,
            "extension": extension
        }
        qry = ServiceOperationQuery(self, "CreateDocumentWithDefaultName", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def recycle(self):
        """Moves the list to the Recycle Bin and returns the identifier of the new Recycle Bin item."""
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "Recycle", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def start_recycle(self):
        """Moves the list to the Recycle Bin and returns the identifier of the new Recycle Bin item."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "StartRecycle", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def render_list_data(self, view_xml):
        """
        Returns the data for the specified query view.<56> The result is implementation-specific, used for
        providing data to a user interface.

        :param str view_xml:  Specifies the query as XML that conforms to the ViewDefinition type as specified in
            [MS-WSSCAML] section 2.3.2.17.
        """
        return_type = ClientResult(self.context)
        payload = {
            "viewXml": view_xml
        }
        qry = ServiceOperationQuery(self, "RenderListData", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def get_list_data_as_stream(context, list_full_url, parameters=None):
        """
        Returns list data from the specified list url and for the specified query parameters.

        :param office365.sharepoint.client_context.ClientContext context: Client context
        :param str list_full_url: The absolute URL of the list.
        :param RenderListDataParameters parameters: The parameters to be used.
        """
        result = ClientResult(context)
        payload = {
            "listFullUrl": list_full_url,
            "parameters": parameters,
        }
        target_list = context.web.get_list(list_full_url)
        qry = ServiceOperationQuery(target_list, "GetListDataAsStream", None, payload, None, result)
        context.add_query(qry)
        return result

    def bulk_validate_update_list_items(self, item_ids, form_values, new_document_update=True,
                                        checkin_comment=None, folder_path=None):
        """
        Validate and update multiple list items.

        :param list[int] item_ids: A collection of item Ids that need to be updated with the same formValues.
        :param dict form_values: A collection of field internal names and values for the given field.
            If the collection is empty, no update will take place.
        :param bool new_document_update: Indicates whether the list item is a document being updated after upload.
            A value of "true" means yes.
        :param str checkin_comment: The comment of check in if any. It's only applicable when the item is checked out.
        :param str folder_path: Decoded path of the folder where the items belong to. If not provided,
            the server will try to find items to update under root folder.
        """
        return_type = ClientResult(self.context, ClientValueCollection(ListItemFormUpdateValue))
        params = {
            "itemIds": item_ids,
            "formValues": ClientValueCollection(ListItemFormUpdateValue, form_values),
            "bNewDocumentUpdate": new_document_update,
            "checkInComment": checkin_comment,
            "folderPath": folder_path
        }
        qry = ServiceOperationQuery(self, "BulkValidateUpdateListItems", None, params, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_lookup_field_choices(self, target_field_name, paging_info=None):
        """

        :param str target_field_name:
        :param str paging_info:
        """
        return_type = ClientResult(self.context, str())
        params = {
            "targetFieldName": target_field_name,
            "pagingInfo": paging_info
        }
        qry = ServiceOperationQuery(self, "GetLookupFieldChoices", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_list_item_changes_since_token(self, query):
        """
        Returns the changes made to the list since the date and time specified in the change token defined
        by the query input parameter.<57>

        :type query: office365.sharepoint.changes.log_item_query.ChangeLogItemQuery
        """
        return_type = ClientResult(self.context, bytes())
        payload = {"query": query}
        qry = ServiceOperationQuery(self, "getListItemChangesSinceToken", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def save_as_new_view(self, old_name, new_name, private_view, uri):
        """
        Overwrites a view if it already exists, creates a new view if it does not; and then extracts the
        implementation-specific filter and sort information from the URL and builds and updates the view's XML.
        Returns the URL of the view.

        :param str old_name: The name of the view the user is currently on.
        :param str new_name: The new name given by the user.
        :param bool private_view: Set to "true" to make the view private; otherwise, "false".
        :param str uri: URL that contains all the implementation-specific filter and sort information for the view.
        """
        payload = {
            "oldName": old_name,
            "newName": new_name,
            "privateView": private_view,
            "uri": uri
        }
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "SaveAsNewView", None, payload, None, return_type)
        self.context.add_query(qry)
        return self

    def save_as_template(self, file_name, name, description, save_data):
        """
        Saves the list as a template in the list template gallery and includes the option of saving with or
        without the data that is contained in the current list.

        :param bool save_data: true to save the data of the original list along with the list template; otherwise, false
        :param str description: A string that contains the description for the list template.
        :param str name: A string that contains the title for the list template.
        :param str file_name: A string that contains the file name for the list template with an .stp extension.
        :return:
        """
        payload = {
            "strFileName": file_name,
            "strName": name,
            "strDescription": description,
            "bSaveData": save_data
        }
        qry = ServiceOperationQuery(self, "saveAsTemplate", None, payload, None, None)
        self.context.add_query(qry)
        return self

    def get_item_by_unique_id(self, unique_id):
        """
        Returns the list item with the specified ID.

        :param str unique_id: The unique ID that is associated with the list item.
        """
        return ListItem(self.context,
                        ServiceOperationPath("getItemByUniqueId", [unique_id], self.resource_path))

    def get_web_dav_url(self, source_url):
        """
        Gets the trusted URL for opening the folder in Explorer view.

        :param str source_url: The URL of the current folder the user is in.
        :return: ClientResult
        """

        return_type = ClientResult(self.context, str())
        payload = {
            "sourceUrl": source_url
        }
        qry = ServiceOperationQuery(self, "getWebDavUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_items(self, caml_query=None):
        """Returns a collection of items from the list based on the specified query.

        :type caml_query: CamlQuery
        """
        if not caml_query:
            caml_query = CamlQuery.create_all_items_query()
        return_type = ListItemCollection(self.context, self.items.resource_path)
        payload = {"query": caml_query}
        qry = ServiceOperationQuery(self, "GetItems", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_item(self, creation_information):
        """The recommended way to add a list item is to send a POST request to the ListItemCollection resource endpoint,
         as shown in ListItemCollection request examples.

         :type creation_information: ListItemCreationInformation or dict"""
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
                creation_information.FolderUrl = self.context.base_url + self.root_folder.serverRelativeUrl
                payload = {"parameters": creation_information}
                next_qry = ServiceOperationQuery(self, "addItem", None, payload, None, return_type)
                self.context.add_query(next_qry)

            self.root_folder.ensure_property("ServerRelativeUrl", _add_item)
        return return_type

    def create_wiki_page(self, page_name, page_content):
        """
        Creates a wiki page.

        :param str page_name:
        :param str page_content:
        """
        return_type = File(self.context)

        def _root_folder_loaded():
            page_url = self.root_folder.serverRelativeUrl + "/" + page_name
            wiki_props = WikiPageCreationInformation(page_url, page_content)
            Utility.create_wiki_page_in_context_web(self.context, wiki_props, return_type)
        self.ensure_property("RootFolder", _root_folder_loaded)
        return return_type

    def add_item_using_path(self, leaf_name, object_type, folder_url):
        """
        Adds a ListItem to an existing List.

        :param str leaf_name: Specifies the name of the list item that will be created. In the case of a
            document library, the name is equal to the filename of the list item.
        :param int object_type: Specifies the file system object type for the item that will be created.
            It MUST be either FileSystemObjectType.File or FileSystemObjectType.Folder.
        :param str ot None folder_url: Specifies the url of the folder of the new list item.
            The value MUST be either null or the decoded url value an empty string or a server-relative
            URL or an absolute URL. If the value is not null or the decoded url value not being empty string,
            the decoded url value MUST point to a location within the list.
        """
        parameters = ListItemCreationInformationUsingPath(leaf_name, object_type, folder_path=folder_url)
        return_type = ListItem(self.context)
        payload = {"parameters": parameters}
        qry = ServiceOperationQuery(self, "AddItemUsingPath", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_validate_update_item(self, create_info, form_values=None):
        """
        Adds an item to an existing list and validate the list item update values. If all fields validated successfully,
         commit all changes. If there's any exception in any of the fields, the item will not be committed.

        :param ListItemCreationInformation create_info:  Contains the information that determines how the item
            will be created.
        :param dict form_values: A collection of field internal names and values for the given field. If the collection
            is empty, no update will take place.
        """
        payload = {
            "listItemCreateInfo": create_info,
            "formValues": [ListItemFormUpdateValue(k, v) for k, v in form_values.items()]
        }
        return_type = ClientResult(self.context, ClientValueCollection(ListItemFormUpdateValue))
        qry = ServiceOperationQuery(self, "AddValidateUpdateItem", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_item_by_id(self, item_id):
        """Returns the list item with the specified list item identifier.

        :type item_id: int
        """
        return ListItem(self.context, ServiceOperationPath("getItemById", [item_id], self.resource_path))

    def get_view(self, view_id):
        """Returns the list view with the specified view identifier.

        :type view_id: str
        """
        return View(self.context, ServiceOperationPath("getView", [view_id], self.resource_path), self)

    def get_changes(self, query=None):
        """Returns the collection of changes from the change log that have occurred within the list,
           based on the specified query.

        :param office365.sharepoint.changeQuery.ChangeQuery query: Specifies which changes to return
        """
        if query is None:
            query = ChangeQuery(list_=True)
        return_type = ChangeCollection(self.context)
        payload = {"query": query}
        qry = ServiceOperationQuery(self, "getChanges", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_checked_out_files(self):
        """Returns a collection of checked-out files as specified in section 3.2.5.381."""
        return_type = CheckedOutFileCollection(self.context)
        qry = ServiceOperationQuery(self, "GetCheckedOutFiles", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def reserve_list_item_id(self):
        """
        Reserves the returned list item identifier for the idempotent creation of a list item.
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "ReserveListItemId", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_related_fields(self):
        """
        Returns a collection of lookup fields that use this list as a data source and
        that have FieldLookup.IsRelationship set to true.
        """
        return RelatedFieldCollection(self.context, ServiceOperationPath("getRelatedFields", [], self.resource_path))

    def get_special_folder_url(self, folder_type, force_create, existing_folder_guid):
        """
        Gets the relative URL of the Save to OneDrive folder.

        :param int folder_type: The Save-to-OneDrive type.
        :param bool force_create: Specify true if the folder doesn't exist and SHOULD be created.
        :param str existing_folder_guid:  The GUID of the created folders that exist, if any.
        """
        payload = {
            "type": folder_type,
            "bForceCreate": force_create,
            "existingFolderGuid": existing_folder_guid
        }
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetSpecialFolderUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def id(self):
        """
        Gets a value that specifies the list identifier.

        :rtype: str
        """
        return self.properties.get("Id", None)

    @property
    def author(self):
        """Specifies the user who created the list."""
        return self.properties.get('Author',
                                   User(self.context, ResourcePath("Author", self.resource_path)))

    @property
    def allow_content_types(self):
        """
        Specifies whether the list supports content types.

        :rtype: bool or None
        """
        return self.properties.get("AllowContentTypes", None)

    @property
    def base_template(self):
        """
        Specifies the list server template of the list.

        :rtype: int or None
        """
        return self.properties.get("BaseTemplate", None)

    @property
    def base_type(self):
        """
        Specifies the base type of the list.
        It MUST be one of the following values: GenericList, DocumentLibrary, DiscussionBoard, Survey, or Issue.

        :rtype: int or None
        """
        return self.properties.get("BaseType", None)

    @property
    def default_display_form_url(self):
        """
        Specifies the location of the default display form for the list.

        :rtype: str or None
        """
        return self.properties.get("DefaultDisplayFormUrl", None)

    @property
    def default_view_path(self):
        """
        Specifies the server-relative URL of the default view for the list.
        """
        return self.properties.get("DefaultViewPath", SPResPath())

    @property
    def default_view_url(self):
        """
        Specifies the server-relative URL of the default view for the list.

        :rtype: str or None
        """
        return self.properties.get("DefaultViewUrl", None)

    @property
    def crawl_non_default_views(self):
        """
        Specifies whether or not the crawler indexes the non-default views of the list.
        Specify a value of true if the crawler indexes the list's non-default views; specify false if otherwise.

        :rtype: bool or None
        """
        return self.properties.get("CrawlNonDefaultViews", None)

    @property
    def creatables_info(self):
        """
        Returns an object that describes what this list can create, and a collection of links to visit in order to
        create those things. If it can't create certain things, it contains an error message describing why.

         The consumer MUST append the encoded URL of the current page to the links returned here.
         (This page the link goes to needs it as a query parameter to function correctly.)
         The consumer SHOULD also consider appending &IsDlg=1 to the link, to remove the UI from the linked page,
         if desired.
        """
        return self.properties.get('CreatablesInfo',
                                   CreatablesInfo(self.context, ResourcePath("CreatablesInfo", self.resource_path)))

    @property
    def current_change_token(self):
        """Gets the current change token that is used in the change log for the list."""
        return self.properties.get("CurrentChangeToken", ChangeToken())

    @property
    def data_source(self):
        """
        Specifies the data source of an external list.
        If HasExternalDataSource is "false", the server MUST return NULL.
        """
        return self.properties.get("DataSource", ListDataSource())

    @property
    def enable_folder_creation(self):
        """
        Specifies whether new list folders can be added to the list.

        :rtype: bool or None
        """
        return self.properties.get("EnableFolderCreation", None)

    @property
    def default_edit_form_url(self):
        """
        Gets a value that specifies the URL of the edit form to use for list items in the list.

        :rtype: str or None
        """
        return self.properties.get("DefaultEditFormUrl", None)

    @property
    def default_item_open_in_browser(self):
        """
        :rtype: bool or None
        """
        return self.properties.get("DefaultItemOpenInBrowser", None)

    @enable_folder_creation.setter
    def enable_folder_creation(self, value):
        self.set_property("EnableFolderCreation", value, True)

    @property
    def items(self):
        """Get list items"""
        return self.properties.get("Items",
                                   ListItemCollection(self.context, ResourcePath("items", self.resource_path)))

    @property
    def root_folder(self):
        """Get a root folder"""
        return self.properties.get("RootFolder",
                                   Folder(self.context, ResourcePath("RootFolder", self.resource_path)))

    @property
    def fields(self):
        """Gets a value that specifies the collection of all fields in the list."""
        return self.properties.get('Fields',
                                   FieldCollection(self.context, ResourcePath("Fields", self.resource_path), self))

    @property
    def subscriptions(self):
        """Gets one or more webhook subscriptions on a SharePoint list."""
        return self.properties.get('Subscriptions',
                                   SubscriptionCollection(self.context,
                                                          ResourcePath("Subscriptions", self.resource_path), self))

    @property
    def views(self):
        """Gets a value that specifies the collection of all public views on the list and personal views
        of the current user on the list."""
        return self.properties.get('Views',
                                   ViewCollection(self.context, ResourcePath("views", self.resource_path), self))

    @property
    def default_view(self):
        """Gets or sets a value that specifies whether the list view is the default list view."""
        return self.properties.get('DefaultView',
                                   View(self.context, ResourcePath("DefaultView", self.resource_path), self))

    @property
    def content_types(self):
        """Gets the content types that are associated with the list."""
        return self.properties.get('ContentTypes',
                                   ContentTypeCollection(self.context,
                                                         ResourcePath("ContentTypes", self.resource_path), self))

    @property
    def content_types_enabled(self):
        """Specifies whether content types are enabled for the list.

        :rtype: bool or None
        """
        return self.properties.get('ContentTypesEnabled', None)

    @property
    def user_custom_actions(self):
        """Gets the User Custom Actions that are associated with the list."""
        return self.properties.get('UserCustomActions',
                                   UserCustomActionCollection(self.context,
                                                              ResourcePath("UserCustomActions", self.resource_path)))

    @property
    def custom_action_elements(self):
        return self.properties.get('CustomActionElements', CustomActionElementCollection())

    @property
    def forms(self):
        """Gets a value that specifies the collection of all list forms in the list."""
        return self.properties.get('Forms',
                                   FormCollection(self.context, ResourcePath("forms", self.resource_path)))

    @property
    def parent_web(self):
        """Gets a value that specifies the web where list resides."""
        from office365.sharepoint.webs.web import Web
        return self.properties.get('ParentWeb',
                                   Web(self.context, ResourcePath("parentWeb", self.resource_path)))

    @property
    def event_receivers(self):
        """Get Event receivers"""
        return self.properties.get('EventReceivers',
                                   EventReceiverDefinitionCollection(self.context,
                                                                     ResourcePath("eventReceivers", self.resource_path),
                                                                     self))

    @property
    def item_count(self):
        """Gets a value that specifies the number of list items in the list.

        :rtype: int or None
        """
        return self.properties.get('ItemCount', None)

    @property
    def title(self):
        """Gets the displayed title for the list.

        :rtype: str or None
        """
        return self.properties.get('Title', None)

    @title.setter
    def title(self, val):
        """Sets the displayed title for the list."""
        self.set_property('Title', val)

    @property
    def description(self):
        """Gets the description for the list.
        :rtype: str or None
        """
        return self.properties.get('Description', None)

    @description.setter
    def description(self, val):
        """Sets the description for the list."""
        self.set_property('Description', val)

    @property
    def description_resource(self):
        """Represents the description of this list."""
        return self.properties.get('DescriptionResource',
                                   UserResource(self.context, ResourcePath("DescriptionResource", self.resource_path)))

    @property
    def parent_web_path(self):
        """Returns the path of the parent web for the list."""
        return self.properties.get('ParentWebPath', SPResPath())

    @property
    def schema_xml(self):
        """Specifies the list schema of the list.

        :rtype: str or None
        """
        return self.properties.get("SchemaXml", None)

    @property
    def template_feature_id(self):
        """
        Specifies the feature identifier of the feature that contains the list schema for the list.
        It MUST be an empty GUID if the list schema for the list is not contained within a feature.

        :rtype: str or None
        """
        return self.properties.get("TemplateFeatureId", None)

    @property
    def title_resource(self):
        """Represents the title of this list."""
        return self.properties.get('TitleResource',
                                   UserResource(self.context, ResourcePath("TitleResource", self.resource_path)))

    @property
    def validation_formula(self):
        """
        Specifies the data validation criteria for a list item.

        :rtype: str or None
        """
        return self.properties.get("ValidationFormula", None)

    @property
    def parent_collection(self):
        """
        :rtype: office365.sharepoint.lists.collection.ListCollection
        """
        return self._parent_collection

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "CreatablesInfo": self.creatables_info,
                "CurrentChangeToken": self.current_change_token,
                "ContentTypes": self.content_types,
                "CustomActionElements": self.custom_action_elements,
                "DataSource": self.data_source,
                "DescriptionResource": self.description_resource,
                "DefaultView": self.default_view,
                "DefaultViewPath": self.default_view_path,
                "EventReceivers": self.event_receivers,
                "ParentWeb": self.parent_web,
                "ParentWebPath": self.parent_web_path,
                "RootFolder": self.root_folder,
                "TitleResource": self.title_resource,
                "UserCustomActions": self.user_custom_actions
            }
            default_value = property_mapping.get(name, None)
        return super(List, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(List, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id":
                self._resource_path = self.parent_collection.get_by_id(value).resource_path
        return self
