from office365.onedrive.listItemCollection import ListItemCollection
from office365.runtime.auth.ClientCredential import ClientCredential
from office365.runtime.auth.UserCredential import UserCredential
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.client_query import DeleteEntityQuery, UpdateEntityQuery
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.odata.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel
from office365.runtime.odata.odata_request import ODataRequest
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.listitem import ListItem


class ListDataService(ClientRuntimeContext):
    """SharePoint 2010 list data service"""

    def __init__(self, base_url, auth_context):
        if base_url.endswith("/"):
            base_url = base_url[:len(base_url) - 1]
        super(ListDataService, self).__init__(base_url + "/_vti_bin/listdata.svc/", auth_context)
        self._pendingRequest = ODataRequest(self, JsonLightFormat(ODataMetadataLevel.Verbose))

    @classmethod
    def connect_with_credentials(cls, base_url, credentials):
        ctx_auth = AuthenticationContext(url=base_url)
        if isinstance(credentials, ClientCredential):
            ctx_auth.acquire_token_for_app(client_id=credentials.clientId, client_secret=credentials.clientSecret)
        elif isinstance(credentials, UserCredential):
            ctx_auth.acquire_token_for_user(username=credentials.userName, password=credentials.password)
        else:
            raise ValueError("Unknown credential type")
        return cls(base_url, ctx_auth)

    def get_pending_request(self):
        return self._pendingRequest

    def get_list_items(self, list_name):
        return ListItemCollection(self, ResourcePathServiceOperation(list_name, None, None))

    def get_list_item(self, list_name, item_id):
        return ListItem(self,
                        ResourcePathServiceOperation(list_name, [item_id], None))

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
