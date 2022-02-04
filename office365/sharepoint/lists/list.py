from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.changes.change_collection import ChangeCollection
from office365.sharepoint.changes.change_query import ChangeQuery
from office365.sharepoint.contenttypes.content_type_collection import ContentTypeCollection
from office365.sharepoint.customactions.custom_action_element import CustomActionElement
from office365.sharepoint.eventreceivers.event_receiver_definition import EventReceiverDefinitionCollection
from office365.sharepoint.fields.field_collection import FieldCollection
from office365.sharepoint.fields.related_field_collection import RelatedFieldCollection
from office365.sharepoint.files.checkedOutFileCollection import CheckedOutFileCollection
from office365.sharepoint.files.file import File
from office365.sharepoint.flows.flow_synchronization_result import FlowSynchronizationResult
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.forms.form_collection import FormCollection
from office365.sharepoint.listitems.caml.caml_query import CamlQuery
from office365.sharepoint.listitems.creation_information_using_path import ListItemCreationInformationUsingPath
from office365.sharepoint.listitems.form_update_value import ListItemFormUpdateValue
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.listitems.listItem_collection import ListItemCollection
from office365.sharepoint.lists.list_rule import SPListRule
from office365.sharepoint.pages.wiki_page_creation_information import WikiPageCreationInformation
from office365.sharepoint.permissions.securable_object import SecurableObject
from office365.sharepoint.usercustomactions.user_custom_action_collection import UserCustomActionCollection
from office365.sharepoint.views.view import View
from office365.sharepoint.views.view_collection import ViewCollection
from office365.sharepoint.webhooks.subscription_collection import SubscriptionCollection
from office365.sharepoint.utilities.utility import Utility


class List(SecurableObject):
    """Represents a list on a SharePoint Web site."""

    def __init__(self, context, resource_path=None):
        super(List, self).__init__(context, resource_path)

    def get_all_rules(self):
        return_type = ClientResult(self.context, ClientValueCollection(SPListRule))
        qry = ServiceOperationQuery(self, "GetAllRules", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_business_app_operation_status(self):
        return_type = FlowSynchronizationResult(self.context)
        qry = ServiceOperationQuery(self, "GetBusinessAppOperationStatus", None, None, None, return_type)
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
        :param str folder_path:
        :param str extension:
        """
        return_type = FlowSynchronizationResult(self.context)
        payload = {
            "folderPath": folder_path,
            "extension": extension
        }
        qry = ServiceOperationQuery(self, "CreateDocumentWithDefaultName", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def recycle(self):
        """Moves the list to the Recycle Bin and returns the identifier of the new Recycle Bin item."""
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "Recycle", None, None, None, result)
        self.context.add_query(qry)
        return result

    def render_list_data(self, view_xml):
        """

        :param str view_xml: View xml
        """
        result = ClientResult(self.context)
        payload = {
            "viewXml": view_xml
        }
        qry = ServiceOperationQuery(self, "RenderListData", None, payload, None, result)
        self.context.add_query(qry)
        return result

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
        result = ClientValueCollection(ListItemFormUpdateValue)
        params = {
            "itemIds": item_ids,
            "formValues": ClientValueCollection(ListItemFormUpdateValue, form_values),
            "bNewDocumentUpdate": new_document_update,
            "checkInComment": checkin_comment,
            "folderPath": folder_path
        }
        qry = ServiceOperationQuery(self, "BulkValidateUpdateListItems", None, params, None, result)
        self.context.add_query(qry)
        return result

    def get_lookup_field_choices(self, target_field_name, paging_info=None):
        """

        """
        result = ClientResult(self.context)
        params = {
            "targetFieldName": target_field_name,
            "pagingInfo": paging_info
        }
        qry = ServiceOperationQuery(self, "GetLookupFieldChoices", params, None, None, result)
        self.context.add_query(qry)
        return result

    def get_list_item_changes_since_token(self, query):
        """
        Returns the changes made to the list since the date and time specified in the change token defined
        by the query input parameter.<57>

        :type query: office365.sharepoint.changes.change_log_item_query.ChangeLogItemQuery
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "getListItemChangesSinceToken", None, query, "query", result)
        self.context.add_query(qry)
        return result

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

        :param str unique_id:

        """
        return ListItem(self.context,
                        ServiceOperationPath("getItemByUniqueId", [unique_id], self.resource_path))

    def get_web_dav_url(self, source_url):
        """
        Gets the trusted URL for opening the folder in Explorer view.

        :param str source_url: The URL of the current folder the user is in.
        :return: ClientResult
        """

        result = ClientResult(self.context)
        payload = {
            "sourceUrl": source_url
        }
        qry = ServiceOperationQuery(self, "getWebDavUrl", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def get_items(self, caml_query=None):
        """Returns a collection of items from the list based on the specified query.

        :type caml_query: CamlQuery
        """
        if not caml_query:
            caml_query = CamlQuery.create_all_items_query()
        items = ListItemCollection(self.context, ResourcePath("items", self.resource_path))
        qry = ServiceOperationQuery(self, "GetItems", None, caml_query, "query", items)
        self.context.add_query(qry)
        return items

    def add_item(self, list_item_creation_information):
        """The recommended way to add a list item is to send a POST request to the ListItemCollection resource endpoint,
         as shown in ListItemCollection request examples.

         :type list_item_creation_information: ListItemCreationInformation or dict"""
        item = ListItem(self.context, None, self)
        if isinstance(list_item_creation_information, dict):
            for k, v in list_item_creation_information.items():
                item.set_property(k, v, True)
            self.items.add_child(item)
            item.ensure_type_name(self)
            qry = ServiceOperationQuery(self, "items", None, item, None, item)
            self.context.add_query(qry)
        else:
            def _resolve_folder_url():
                list_item_creation_information.FolderUrl = self.context.base_url + self.root_folder.serverRelativeUrl
                add_item_qry = ServiceOperationQuery(
                    self,
                    "addItem",
                    None,
                    list_item_creation_information,
                    "parameters",
                    item
                )
                self.context.add_query(add_item_qry)

            self.root_folder.ensure_property("ServerRelativeUrl", _resolve_folder_url)
        return item

    def create_wiki_page(self, page_name, page_content):
        """
        Creates a wiki page.

        :param str page_name:
        :param str page_content:
        """
        result = ClientResult(self.context, File(self.context))

        def _list_loaded():
            page_url = self.root_folder.serverRelativeUrl + "/" + page_name
            wiki_props = WikiPageCreationInformation(page_url, page_content)
            result.value = Utility.create_wiki_page_in_context_web(self.context, wiki_props)
        self.ensure_property("RootFolder", _list_loaded)

        return result

    def add_item_using_path(self, leaf_name, object_type, folder_url):
        """
        :type leaf_name: str
        :type object_type: int
        :type folder_url: str
        """
        from office365.sharepoint.types.resource_path import ResourcePath as SPResPath
        parameters = ListItemCreationInformationUsingPath(leaf_name, object_type, folder_path=SPResPath(folder_url))
        item = ListItem(self.context)
        qry = ServiceOperationQuery(self, "AddItemUsingPath", None, parameters, "parameters", item)
        self.context.add_query(qry)
        return item

    def add_validate_update_item(self):
        pass

    def get_item_by_id(self, item_id):
        """Returns the list item with the specified list item identifier.

        :type item_id: int
        """
        return ListItem(self.context,
                        ServiceOperationPath("getItemById", [item_id], self.resource_path))

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
        changes = ChangeCollection(self.context)
        qry = ServiceOperationQuery(self, "getChanges", None, query, "query", changes)
        self.context.add_query(qry)
        return changes

    def get_checked_out_files(self):
        result = CheckedOutFileCollection(self.context)
        qry = ServiceOperationQuery(self, "GetCheckedOutFiles", None, None, None, result)
        self.context.add_query(qry)
        return result

    def reserve_list_item_id(self):
        """
        Reserves the returned list item identifier for the idempotent creation of a list item.
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "ReserveListItemId", None, None, None, result)
        self.context.add_query(qry)
        return result

    def get_related_fields(self):
        """Returns a collection of lookup fields that use this list as a data source and
            that have FieldLookup.IsRelationship set to true.
        """
        return RelatedFieldCollection(self.context,
                                      ServiceOperationPath("getRelatedFields", [], self.resource_path))

    @property
    def id(self):
        """
        Gets a value that specifies the list identifier.
        :rtype: str
        """
        return self.properties.get("Id", None)

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
    def user_custom_actions(self):
        """Gets the User Custom Actions that are associated with the list."""
        return self.properties.get('UserCustomActions',
                                   UserCustomActionCollection(self.context,
                                                              ResourcePath("UserCustomActions", self.resource_path)))

    @property
    def custom_action_elements(self):
        return self.properties.get('CustomActionElements',
                                   ClientValueCollection(CustomActionElement))

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
    def parent_web_path(self):
        return self.properties.get('ParentWebPath', None)

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "ContentTypes": self.content_types,
                "CustomActionElements": self.custom_action_elements,
                "DefaultView": self.default_view,
                "EventReceivers": self.event_receivers,
                "ParentWeb": self.parent_web,
                "RootFolder": self.root_folder,
                "UserCustomActions": self.user_custom_actions
            }
            default_value = property_mapping.get(name, None)
        return super(List, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(List, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id":
                self._resource_path = ServiceOperationPath(
                    "GetById", [value], self._parent_collection.resource_path)
        return self
