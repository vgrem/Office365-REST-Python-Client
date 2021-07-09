from office365.actions.download_content_query import DownloadContentQuery
from office365.directory.applicationCollection import ApplicationCollection
from office365.directory.directory import Directory
from office365.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.directory.group_collection import GroupCollection
from office365.directory.groupSettingTemplateCollection import GroupSettingTemplateCollection
from office365.directory.identityProviderCollection import IdentityProviderCollection
from office365.directory.organization import Organization
from office365.directory.servicePrincipal import ServicePrincipalCollection
from office365.directory.subscribedSku import SubscribedSkuCollection
from office365.directory.user import User
from office365.directory.userCollection import UserCollection
from office365.onedrive.driveCollection import DriveCollection
from office365.onedrive.sharedDriveItemCollection import SharedDriveItemCollection
from office365.onedrive.siteCollection import SiteCollection
from office365.mail.contact_collection import ContactCollection
from office365.runtime.auth.token_response import TokenResponse
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.odata_request import ODataRequest
from office365.runtime.odata.odata_v4_batch_request import ODataV4BatchRequest
from office365.runtime.odata.v4_json_format import V4JsonFormat
from office365.runtime.queries.batch_query import BatchQuery
from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.queries.update_entity_query import UpdateEntityQuery
from office365.runtime.resource_path import ResourcePath
from office365.teams.team_collection import TeamCollection


class GraphClient(ClientRuntimeContext):
    """Graph client"""

    def __init__(self, acquire_token_callback):
        """

        :param () -> dict acquire_token_callback: Acquire token function
        """
        super(GraphClient, self).__init__()
        self._pending_request = ODataRequest(self, V4JsonFormat("minimal"))
        self._pending_request.beforeExecute += self._build_specific_query
        self._resource = "https://graph.microsoft.com"
        self._authority_host_url = "https://login.microsoftonline.com"
        self._acquire_token_callback = acquire_token_callback

    def build_single_request(self, query):
        """
        :type: office365.runtime.queries.client_query.ClientQuery
        """
        request = super(GraphClient, self).build_single_request(query)
        self._build_specific_query(request)
        return request

    def execute_batch(self):
        """Construct and submit a batch request"""
        batch_request = ODataV4BatchRequest(self)
        queries = [qry for qry in self.pending_request()]
        batch_qry = BatchQuery(self, queries)  # Aggregate requests into batch request
        batch_request.execute_query(batch_qry)

    def pending_request(self):
        return self._pending_request

    def service_root_url(self):
        return "https://graph.microsoft.com/v1.0"

    def _build_specific_query(self, request):
        """
        Builds Graph specific request

        :type request: RequestOptions
        """
        query = self.current_query
        if isinstance(query, UpdateEntityQuery):
            request.method = HttpMethod.Patch
        elif isinstance(query, DeleteEntityQuery):
            request.method = HttpMethod.Delete
        if isinstance(query, DownloadContentQuery):
            request.method = HttpMethod.Get

    def authenticate_request(self, request):
        """

        :type request: RequestOptions
        """
        token_json = self._acquire_token_callback()
        token = TokenResponse.from_json(token_json)
        request.set_header('Authorization', 'Bearer {0}'.format(token.accessToken))

    def execute_request(self, url_or_options):
        """
        Constructs and submits request directly

        :type url_or_options: str or RequestOptions
        """
        if not isinstance(url_or_options, RequestOptions):
            url_or_options = RequestOptions("{0}/{1}".format(self.service_root_url(), url_or_options))
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
    def directory_objects(self):
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

    @property
    def identity_providers(self):
        """Represents a deleted item in the directory"""
        return IdentityProviderCollection(self, ResourcePath("identityProviders"))

    @property
    def applications(self):
        """Get the list of applications in this organization."""
        return ApplicationCollection(self, ResourcePath("applications"))

    @property
    def service_principals(self):
        """Retrieve a list of servicePrincipal objects."""
        return ServicePrincipalCollection(self, ResourcePath("servicePrincipals"))

    @property
    def organization(self):
        return Organization(self, ResourcePath("organization"))

    @property
    def subscribed_skus(self):
        """Retrieve a list of servicePrincipal objects."""
        return SubscribedSkuCollection(self, ResourcePath("subscribedSkus"))
