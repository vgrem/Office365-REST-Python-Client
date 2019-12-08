from office365.runtime.client_query import ClientQuery, DeleteEntityQuery, UpdateEntityQuery
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.odata.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.listitem import ListItem


class ListDataService(ClientRuntimeContext):
    """SharePoint 2010 list data service"""

    def __init__(self, base_url, auth_context):
        if base_url.endswith("/"):
            base_url = base_url[:len(base_url) - 1]
        super(ListDataService, self).__init__(base_url + "/_vti_bin/listdata.svc/", auth_context)
        self.json_format = JsonLightFormat(ODataMetadataLevel.Verbose)

    def get_list_item(self, list_name, item_id):
        return ListItem(self,
                        ResourcePathServiceOperation(self, None, list_name, [item_id]))

    def delete_list_item(self, list_name, item_id):
        list_item_to_delete = self.get_list_item(list_name, item_id)
        qry = DeleteEntityQuery(list_item_to_delete)
        self.add_query(qry)

    def update_list_item(self, list_name, item_id, field_values):
        list_item_to_update = self.get_list_item(list_name, item_id)
        for name, value in field_values:
            list_item_to_update.set_property(name, value)
        qry = UpdateEntityQuery(list_item_to_update)
        self.add_query(qry)
