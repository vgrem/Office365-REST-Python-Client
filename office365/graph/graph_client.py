import adal

from office365.graph.directory.directory import Directory
from office365.graph.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.graph.directory.groupCollection import GroupCollection
from office365.graph.directory.groupSettingTemplateCollection import GroupSettingTemplateCollection
from office365.graph.directory.userCollection import UserCollection
from office365.graph.one_drive_actions import DownloadContentQuery, UploadContentQuery, ReplaceMethodQuery, SearchQuery
from office365.graph.onedrive.sharedDriveItemCollection import SharedDriveItemCollection
from office365.graph.onedrive.siteCollection import SiteCollection
from office365.outlookservices.contact_collection import ContactCollection
from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.odata.odata_request import ODataRequest
from office365.runtime.odata.v4_json_format import V4JsonFormat
from office365.runtime.resource_path import ResourcePath
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.graph.directory.user import User
from office365.graph.onedrive.driveCollection import DriveCollection
from office365.graph.teams.teamCollection import TeamCollection


class GraphClient(ClientRuntimeContext):
    """Graph client"""

    def __init__(self, tenant, acquire_token_callback):
        """

        :param (adal.AuthenticationContext) -> dict acquire_token_callback: Acquire token function
        :param str tenant: Tenant name
        """
        self.__service_root_url = "https://graph.microsoft.com/v1.0/"
        super(GraphClient, self).__init__(self.__service_root_url)
        self._pending_request = ODataRequest(self, V4JsonFormat("minimal"))
        self._pending_request.beforeExecute += self._build_specific_query
        self._resource = "https://graph.microsoft.com"
        self._authority_host_url = "https://login.microsoftonline.com"
        self._tenant = tenant
        self._acquire_token_callback = acquire_token_callback

    def get_pending_request(self):
        return self._pending_request

    def _build_specific_query(self, request):
        """
        Builds Graph specific request

        :type request: RequestOptions
        """
        query = self.get_pending_request().current_query
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
        """

        :type request: RequestOptions
        """
        authority_url = self._authority_host_url + '/' + self._tenant
        auth_ctx = adal.AuthenticationContext(authority_url)
        token = self._acquire_token_callback(auth_ctx)
        request.set_header('Authorization', 'Bearer {0}'.format(token["accessToken"]))

    def execute_request(self, url_or_options):
        """
        Constructs and submits request directly

        :type url_or_options: str or RequestOptions
        """
        if not isinstance(url_or_options, RequestOptions):
            url_or_options = RequestOptions("{0}/{1}".format(self.__service_root_url, url_or_options))
        return self.execute_request_direct(url_or_options)

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

    @property
    def teams(self):
        """Get teams"""
        return TeamCollection(self, ResourcePath("teams"))

    @property
    def groupSettingTemplates(self):
        """Get teams"""
        return GroupSettingTemplateCollection(self, ResourcePath("groupSettingTemplates"))

    @property
    def contacts(self):
        """o get all the contacts in a user's mailbox"""
        return ContactCollection(self, ResourcePath("contacts"))

    @property
    def directory(self):
        """Represents a deleted item in the directory"""
        return Directory(self, ResourcePath("directory"))

