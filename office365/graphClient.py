import adal

from office365.directory.directoryObject import DirectoryObject
from office365.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.onedrive.siteCollection import SiteCollection
from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.odata.v4_json_format import V4JsonFormat
from office365.runtime.resource_path_entity import ResourcePathEntity
from office365.runtime.utilities.http_method import HttpMethod
from office365.runtime.utilities.request_options import RequestOptions
from office365.directory.user import User
from office365.onedrive.sharedDriveItem import SharedDriveItem
from office365.directory.groupCollection import GroupCollection
from office365.directory.userCollection import UserCollection
from office365.onedrive.driveCollection import DriveCollection
from office365.onedrive.sharedDriveItemCollection import SharedDriveItemCollection


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

    def execute_query(self):
        self.pending_request.before_execute_query(self._build_specific_query)
        super(GraphClient, self).execute_query()

    @staticmethod
    def _build_specific_query(request, query):
        if isinstance(query, UpdateEntityQuery):
            request.method = HttpMethod.Patch
        elif isinstance(query, DeleteEntityQuery):
            request.method = HttpMethod.Delete

    def authenticate_request(self, request):
        authority_url = self._authority_host_url + '/' + self._tenant
        auth_ctx = adal.AuthenticationContext(authority_url)
        token = self._acquire_token_callback(auth_ctx)
        request.set_header('Authorization', 'Bearer {0}'.format(token["accessToken"]))

    def execute_request(self, url):
        request = RequestOptions("{0}/{1}".format(self.__service_root_url, url))
        return self.execute_request_direct(request)

    @property
    def me(self):
        """The Me endpoint is provided as a shortcut for specifying the current user"""
        return User(self, ResourcePathEntity(self, None, "me"))

    @property
    def drives(self):
        """Get one drives"""
        return DriveCollection(self, ResourcePathEntity(self, None, "drives"))

    @property
    def users(self):
        """Get users"""
        return UserCollection(self, ResourcePathEntity(self, None, "users"))

    @property
    def groups(self):
        """Get groups"""
        return GroupCollection(self, ResourcePathEntity(self, None, "groups"))

    @property
    def sites(self):
        """Get sites"""
        return SiteCollection(self, ResourcePathEntity(self, None, "sites"))

    @property
    def shares(self):
        """Get shares"""
        return SharedDriveItemCollection(self, ResourcePathEntity(self, SharedDriveItem, "shares"))

    @property
    def directoryObjects(self):
        """Get Directory Objects"""
        return DirectoryObjectCollection(self, ResourcePathEntity(self, DirectoryObject, "directoryObjects"))
