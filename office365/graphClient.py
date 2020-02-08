import adal
from office365.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.onedrive.siteCollection import SiteCollection
from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery, ServiceOperationQuery
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.odata.v4_json_format import V4JsonFormat
from office365.runtime.resource_path import ResourcePath
from office365.runtime.utilities.http_method import HttpMethod
from office365.runtime.utilities.request_options import RequestOptions
from office365.directory.user import User
from office365.directory.groupCollection import GroupCollection
from office365.directory.userCollection import UserCollection
from office365.onedrive.driveCollection import DriveCollection
from office365.onedrive.sharedDriveItemCollection import SharedDriveItemCollection


class DownloadContentQuery(ServiceOperationQuery):
    def __init__(self, entity_type, format_name=None):
        action_name = "content"
        if format_name is not None:
            action_name = action_name + r"?format={0}".format(format_name)
        super(DownloadContentQuery, self).__init__(entity_type, action_name, None, None)


class ReplaceMethodQuery(ServiceOperationQuery):
    pass


class UploadContentQuery(ServiceOperationQuery):
    def __init__(self, entity_type, content=None):
        super(UploadContentQuery, self).__init__(entity_type, "content", None, content)


class SearchQuery(ServiceOperationQuery):
    def __init__(self, entity_type, query_text):
        super(SearchQuery, self).__init__(entity_type, "search", {"q": query_text}, None)


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
        self.pending_request.before_execute_request(self._build_specific_query)
        super(GraphClient, self).execute_query()

    @staticmethod
    def _build_specific_query(request, query):
        if isinstance(query, UpdateEntityQuery):
            request.method = HttpMethod.Patch
        elif isinstance(query, DeleteEntityQuery):
            request.method = HttpMethod.Delete
        if isinstance(query, DownloadContentQuery):
            request.method = HttpMethod.Get
        elif isinstance(query, UploadContentQuery):
            request.method = HttpMethod.Put
        elif isinstance(query, ReplaceMethodQuery):
            request.method = HttpMethod.Patch
        elif isinstance(query, SearchQuery):
            request.method = HttpMethod.Get

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
        return User(self, ResourcePath("me"))

    @property
    def drives(self):
        """Get one drives"""
        return DriveCollection(self, ResourcePath("drives"))

    @property
    def users(self):
        """Get users"""
        return UserCollection(self, ResourcePath("users"))

    @property
    def groups(self):
        """Get groups"""
        return GroupCollection(self, ResourcePath("groups"))

    @property
    def sites(self):
        """Get sites"""
        return SiteCollection(self, ResourcePath("sites"))

    @property
    def shares(self):
        """Get shares"""
        return SharedDriveItemCollection(self, ResourcePath("shares"))

    @property
    def directoryObjects(self):
        """Get Directory Objects"""
        return DirectoryObjectCollection(self, ResourcePath("directoryObjects"))
