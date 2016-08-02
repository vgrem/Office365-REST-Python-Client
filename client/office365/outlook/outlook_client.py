from client.office365.outlook.contact_collection import ContactCollection
from client.office365.runtime.auth.network_credential_context import NetworkCredentialContext
from client.office365.runtime.client_runtime_context import ClientRuntimeContext
from client.office365.runtime.odata.odata_metadata_level import ODataMetadataLevel
from client.office365.runtime.odata.v4_json_format import V4JsonFormat
from client.office365.runtime.resource_path_entry import ResourcePathEntry


class OutlookClient(ClientRuntimeContext):
    """Office365 Outlook client context"""

    def __init__(self, username, password):
        self.__service_root_url = "https://outlook.office365.com/api/v1.0/"
        ctx_auth = NetworkCredentialContext(username, password)
        super(OutlookClient, self).__init__(self.__service_root_url, ctx_auth)
        self.json_format = V4JsonFormat("minimal")
        self.__root_resource_path = ResourcePathEntry(self, None, "me")

    def get_contacts(self):
        """Get a contact collection from the default Contacts folder of the signed-in user (.../me/contacts),
        or from the specified contact folder."""
        contacts = ContactCollection(self, ResourcePathEntry(self, self.__root_resource_path, "contacts"))
        return contacts
