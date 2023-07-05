from office365.booking.solutions_root import SolutionsRoot
from office365.communications.cloud_communications import CloudCommunications
from office365.delta_collection import DeltaCollection
from office365.directory.applications.collection import ApplicationCollection
from office365.directory.applications.template import ApplicationTemplate
from office365.directory.audit.log_root import AuditLogRoot
from office365.directory.directory import Directory
from office365.directory.domains.domain import Domain
from office365.directory.groups.collection import GroupCollection
from office365.directory.groups.lifecycle_policy import GroupLifecyclePolicy
from office365.directory.groups.setting_template import GroupSettingTemplate
from office365.directory.identities.container import IdentityContainer
from office365.directory.identities.governance import IdentityGovernance
from office365.directory.protection.information import InformationProtection
from office365.directory.protection.root import IdentityProtectionRoot
from office365.directory.identities.provider import IdentityProvider
from office365.directory.internal.paths.me import MePath
from office365.directory.invitations.collection import InvitationCollection
from office365.directory.licenses.subscribed_sku import SubscribedSku
from office365.directory.object_collection import DirectoryObjectCollection
from office365.directory.permissions.grants.resource_specific import ResourceSpecificPermissionGrant
from office365.directory.policies.root import PolicyRoot
from office365.directory.rolemanagement.management import RoleManagement
from office365.directory.rolemanagement.role import DirectoryRole
from office365.directory.security.security import Security
from office365.directory.serviceprincipals.collection import ServicePrincipalCollection
from office365.directory.tenant_relationship import TenantRelationship
from office365.directory.users.collection import UserCollection
from office365.directory.users.user import User
from office365.education.root import EducationRoot
from office365.entity_collection import EntityCollection
from office365.search.external.external import External
from office365.intune.devices.app_management import DeviceAppManagement
from office365.intune.devices.management import DeviceManagement
from office365.intune.organizations.contact import OrgContact
from office365.intune.organizations.organization import Organization
from office365.onedrive.admin import Admin
from office365.onedrive.drives.drive import Drive
from office365.onedrive.shares.collection import SharesCollection
from office365.onedrive.sites.sites_with_root import SitesWithRoot
from office365.outlook.calendar.place import Place
from office365.planner.planner import Planner
from office365.reports.root import ReportRoot
from office365.runtime.auth.token_response import TokenResponse
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.odata.request import ODataRequest
from office365.runtime.odata.v4.batch_request import ODataV4BatchRequest
from office365.runtime.odata.v4.json_format import V4JsonFormat
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.delete_entity import DeleteEntityQuery
from office365.runtime.queries.update_entity import UpdateEntityQuery
from office365.search.entity import SearchEntity
from office365.subscriptions.collection import SubscriptionCollection
from office365.teams.apps.catalog import AppCatalogs
from office365.teams.chats.collection import ChatCollection
from office365.teams.collection import TeamCollection
from office365.teams.template import TeamsTemplate
from office365.teams.viva.employee_experience import EmployeeExperience


class GraphClient(ClientRuntimeContext):
    """Graph Service client"""

    def __init__(self, acquire_token_callback):
        """
        :param () -> dict acquire_token_callback: Acquire token function
        """
        super(GraphClient, self).__init__()
        self._pending_request = None
        self._resource = "https://graph.microsoft.com"
        self._authority_host_url = "https://login.microsoftonline.com"
        self._acquire_token_callback = acquire_token_callback

    def execute_batch(self, items_per_batch=100):
        """Constructs and submit a batch request

        :param int items_per_batch: Maximum to be selected for bulk operation
        """
        batch_request = ODataV4BatchRequest(V4JsonFormat())
        batch_request.beforeExecute += self._authenticate_request
        while self.has_pending_request:
            qry = self._get_next_query(items_per_batch)
            batch_request.execute_query(qry)
        return self

    def pending_request(self):
        if self._pending_request is None:
            self._pending_request = ODataRequest(V4JsonFormat())
            self._pending_request.beforeExecute += self._authenticate_request
            self._pending_request.beforeExecute += self._build_specific_query
        return self._pending_request

    def service_root_url(self):
        return "https://graph.microsoft.com/v1.0"

    def _build_specific_query(self, request):
        """
        Builds Graph specific HTTP request

        :type request: RequestOptions
        """
        if isinstance(self.current_query, UpdateEntityQuery):
            request.method = HttpMethod.Patch
        elif isinstance(self.current_query, DeleteEntityQuery):
            request.method = HttpMethod.Delete

    def _authenticate_request(self, request):
        """
        Authenticate request

        :type request: RequestOptions
        """
        token_json = self._acquire_token_callback()
        token = TokenResponse.from_json(token_json)
        request.ensure_header('Authorization', 'Bearer {0}'.format(token.accessToken))

    @property
    def admin(self):
        """A container for administrator functionality for SharePoint and OneDrive."""
        return Admin(self, ResourcePath("admin"))

    @property
    def app_catalogs(self):
        """A container for apps from the Microsoft Teams app catalog."""
        return AppCatalogs(self, ResourcePath("appCatalogs"))

    @property
    def me(self):
        """The Me endpoint is provided as a shortcut for specifying the current user"""
        return User(self, MePath())

    @property
    def device_management(self):
        """Singleton entity that acts as a container for all device management functionality."""
        return DeviceManagement(self, ResourcePath("deviceManagement"))

    @property
    def device_app_management(self):
        """Singleton entity that acts as a container for all device and app management functionality."""
        return DeviceAppManagement(self, ResourcePath("deviceAppManagement"))

    @property
    def drives(self):
        """Get one drives"""
        return EntityCollection(self, Drive, ResourcePath("drives"))

    @property
    def users(self):
        """Users container"""
        return UserCollection(self, ResourcePath("users"))

    @property
    def domains(self):
        """Alias to domains"""
        return EntityCollection(self, Domain, ResourcePath("domains"))

    @property
    def groups(self):
        """Get groups"""
        return GroupCollection(self, ResourcePath("groups"))

    @property
    def invitations(self):
        """Get invitations"""
        return InvitationCollection(self, ResourcePath("invitations"))

    @property
    def identity_protection(self):
        return IdentityProtectionRoot(self, ResourcePath("identityProtection"))

    @property
    def sites(self):
        """Sites container"""
        return SitesWithRoot(self, ResourcePath("sites"))

    @property
    def shares(self):
        """Shares container"""
        return SharesCollection(self, ResourcePath("shares"))

    @property
    def directory_objects(self):
        """Directory Objects container"""
        return DirectoryObjectCollection(self, ResourcePath("directoryObjects"))

    @property
    def teams(self):
        """Teams container"""
        return TeamCollection(self, ResourcePath("teams"))

    @property
    def chats(self):
        """Chats container"""
        return ChatCollection(self, ResourcePath("chats"))

    @property
    def group_setting_templates(self):
        """Group setting templates represent system-defined settings available to the tenant."""
        return EntityCollection(self, GroupSettingTemplate, ResourcePath("groupSettingTemplates"))

    @property
    def contacts(self):
        """Get the list of organizational contacts for this organization."""
        return DeltaCollection(self, OrgContact, ResourcePath("contacts"))

    @property
    def directory(self):
        """Represents a deleted item in the directory"""
        return Directory(self, ResourcePath("directory"))

    @property
    def directory_roles(self):
        """Represents a directory roles in the directory"""
        return DeltaCollection(self, DirectoryRole, ResourcePath("directoryRoles"))

    @property
    def identity_providers(self):
        return EntityCollection(self, IdentityProvider, ResourcePath("identityProviders"))

    @property
    def identity(self):
        return IdentityContainer(self, ResourcePath("identity"))

    @property
    def application_templates(self):
        """Get the list of application templates in this organization."""
        return EntityCollection(self, ApplicationTemplate, ResourcePath("applicationTemplates"))

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
        """"""
        return EntityCollection(self, Organization, ResourcePath("organization"))

    @property
    def subscribed_skus(self):
        """Get the list of commercial subscriptions that an organization has acquired"""
        return EntityCollection(self, SubscribedSku, ResourcePath("subscribedSkus"))

    @property
    def group_lifecycle_policies(self):
        """A collection of lifecycle policies for a Microsoft 365 groups."""
        return EntityCollection(self, GroupLifecyclePolicy, ResourcePath("groupLifecyclePolicies"))

    @property
    def communications(self):
        """
        Cloud communications API endpoint
        """
        return CloudCommunications(self, ResourcePath("communications"))

    @property
    def identity_governance(self):
        """
        The identity governance singleton
        """
        return IdentityGovernance(self, ResourcePath("identityGovernance"))

    @property
    def information_protection(self):
        """
        Exposes methods that you can use to get Microsoft Purview Information Protection labels and label policies.
        """
        return InformationProtection(self, ResourcePath("informationProtection"))

    @property
    def subscriptions(self):
        """
        Retrieve the properties and relationships of webhook subscriptions,
        based on the app ID, the user, and the user's role with a tenant.
        """
        return SubscriptionCollection(self, ResourcePath("subscriptions"))

    @property
    def tenant_relationships(self):
        """Represent the various type of tenant relationships."""
        return TenantRelationship(self, ResourcePath("tenantRelationships"))

    @property
    def audit_logs(self):
        """
        Get the list of audit logs generated by Azure Active Directory.
        """
        return AuditLogRoot(self, ResourcePath("auditLogs"))

    @property
    def places(self):
        """
        Get all places in a tenant
        """
        return EntityCollection(self, Place, ResourcePath("places"))

    @property
    def reports(self):
        """Represents a container for Azure Active Directory (Azure AD) reporting resources."""
        return ReportRoot(self, ResourcePath("reports"))

    @property
    def role_management(self):
        """Represents a Microsoft 365 role-based access control (RBAC) role management container"""
        return RoleManagement(self, ResourcePath("roleManagement"))

    @property
    def solutions(self):
        return SolutionsRoot(self, ResourcePath("solutions"))

    @property
    def teams_templates(self):
        """
        Get the list of teams templates.
        """
        return EntityCollection(self, TeamsTemplate, ResourcePath("teamsTemplates"))

    @property
    def planner(self):
        """
        The planner resource is the entry point for the Planner object model.
        It returns a singleton planner resource. It doesn't contain any usable properties.
        """
        return Planner(self, ResourcePath("planner"))

    @property
    def permission_grants(self):
        """
        List all resource-specific permission grants
        """
        return EntityCollection(self, ResourceSpecificPermissionGrant, ResourcePath("permissionGrants"))

    @property
    def search(self):
        """
        The search endpoint is the entry point for Microsoft Search API to query data.
        """
        return SearchEntity(self, ResourcePath("search"))

    @property
    def employee_experience(self):
        """
        An alias to EmployeeExperience
        """
        return EmployeeExperience(self, ResourcePath("employeeExperience"))

    @property
    def education(self):
        """
        The /education namespace exposes functionality that is specific to the education sector.
        """
        return EducationRoot(self, ResourcePath("education"))

    @property
    def policies(self):
        """Resource type exposing navigation properties for the policies singleton."""
        return PolicyRoot(self, ResourcePath("policies"))

    @property
    def external(self):
        """A logical container for external sources."""
        return External(self, ResourcePath("external"))

    @property
    def security(self):
        """The security resource is the entry point for the Security object model.
        It returns a singleton security resource. It doesn't contain any usable properties."""
        return Security(self, ResourcePath("security"))
