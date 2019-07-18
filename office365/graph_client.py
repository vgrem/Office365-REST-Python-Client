import adal

from onedrive.drive_collection import DriveCollection
from runtime.client_runtime_context import ClientRuntimeContext
from runtime.odata.v4_json_format import V4JsonFormat
from runtime.resource_path_entry import ResourcePathEntry
from runtime.utilities.request_options import RequestOptions


class GraphClient(ClientRuntimeContext):
    """Graph client"""

    def __init__(self, tenant, acquire_token_callback):
        self.__service_root_url = "https://graph.microsoft.com/v1.0/"
        super(GraphClient, self).__init__(self.__service_root_url, None)
        self.json_format = V4JsonFormat("minimal")
        self._resource = "https://graph.microsoft.com"
        self._authority_host_url = "https://login.microsoftonline.com"
        self._tenant = tenant
        self._acquire_token_callback = acquire_token_callback

    def authenticate_request(self, request):
        authority_url = self._authority_host_url + '/' + self._tenant
        auth_ctx = adal.AuthenticationContext(authority_url)
        token = self._acquire_token_callback(auth_ctx)
        request.set_header('Authorization', 'Bearer {0}'.format(token["accessToken"]))

    def execute_request(self, url):
        request = RequestOptions("{0}/{1}".format(self.__service_root_url, url))
        return self.execute_request_direct(request)

    @property
    def drives(self):
        """Get one drives"""
        return DriveCollection(self, ResourcePathEntry(self, None, "drives"))
