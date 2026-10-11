from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.identitygovernance.entitlementmanagement.accesspackage.catalog import (
    AccessPackageCatalog,
)
from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_request import (
    AccessPackageResourceRequest,
)
from office365.directory.identitygovernance.privilegedaccess.approval import Approval
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.access_package_suggestion import (
        AccessPackageSuggestion,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.assignment import (
        AccessPackageAssignment,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.assignment_policy import (
        AccessPackageAssignmentPolicy,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.assignment_request import (
        AccessPackageAssignmentRequest,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.package import (
        AccessPackage,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource import (
        AccessPackageResource,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_environment import (
        AccessPackageResourceEnvironment,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_role_scope import (
        AccessPackageResourceRoleScope,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.subject import (
        AccessPackageSubject,
    )
    from office365.directory.identitygovernance.entitlementmanagement.available_access_package import (
        AvailableAccessPackage,
    )
    from office365.directory.identitygovernance.entitlementmanagement.connected_organization import (
        ConnectedOrganization,
    )
    from office365.directory.identitygovernance.entitlementmanagement.control_configuration import (
        ControlConfiguration,
    )
    from office365.directory.identitygovernance.entitlementmanagement.external_origin_resource_connector import (
        ExternalOriginResourceConnector,
    )
    from office365.directory.identitygovernance.entitlementmanagement.management_settings import (
        EntitlementManagementSettings,
    )


class EntitlementManagement(Entity):
    """The entitlement management singleton is the container for entitlement management resources,
    including accessPackageCatalog, connectedOrganization, and entitlementManagementSettings.
    """

    @property
    def resource_requests(self):
        """Represents a request to add or remove a resource to or from a catalog respectively."""
        return self.properties.get(
            "resourceRequests",
            EntityCollection(
                self.context, AccessPackageResourceRequest, ResourcePath("resourceRequests", self.resource_path)
            ),
        )

    @property
    def access_package_assignment_approvals(self) -> EntityCollection[Approval]:
        """Gets the accessPackageAssignmentApprovals property"""
        return self.properties.get(
            "accessPackageAssignmentApprovals",
            EntityCollection[Approval](
                self.context, Approval, ResourcePath("accessPackageAssignmentApprovals", self.resource_path)
            ),
        )

    @property
    def catalogs(self) -> EntityCollection[AccessPackageCatalog]:
        """Gets the catalogs property"""
        return self.properties.get(
            "catalogs",
            EntityCollection[AccessPackageCatalog](
                self.context, AccessPackageCatalog, ResourcePath("catalogs", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EntitlementManagement"

    @property
    def access_packages(self) -> EntityCollection[AccessPackage]:
        """Gets the accessPackages property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.package import (
            AccessPackage,
        )

        return self.properties.get(
            "accessPackages",
            EntityCollection[AccessPackage](
                self.context, AccessPackage, ResourcePath("accessPackages", self.resource_path)
            ),
        )

    @property
    def access_package_suggestions(self) -> EntityCollection[AccessPackageSuggestion]:
        """Gets the accessPackageSuggestions property"""
        from office365.directory.identitygovernance.access_package_suggestion import (
            AccessPackageSuggestion,
        )

        return self.properties.get(
            "accessPackageSuggestions",
            EntityCollection[AccessPackageSuggestion](
                self.context, AccessPackageSuggestion, ResourcePath("accessPackageSuggestions", self.resource_path)
            ),
        )

    @property
    def assignment_policies(self) -> EntityCollection[AccessPackageAssignmentPolicy]:
        """Gets the assignmentPolicies property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.assignment_policy import (
            AccessPackageAssignmentPolicy,
        )

        return self.properties.get(
            "assignmentPolicies",
            EntityCollection[AccessPackageAssignmentPolicy](
                self.context, AccessPackageAssignmentPolicy, ResourcePath("assignmentPolicies", self.resource_path)
            ),
        )

    @property
    def assignment_requests(self) -> EntityCollection[AccessPackageAssignmentRequest]:
        """Gets the assignmentRequests property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.assignment_request import (
            AccessPackageAssignmentRequest,
        )

        return self.properties.get(
            "assignmentRequests",
            EntityCollection[AccessPackageAssignmentRequest](
                self.context, AccessPackageAssignmentRequest, ResourcePath("assignmentRequests", self.resource_path)
            ),
        )

    @property
    def assignments(self) -> EntityCollection[AccessPackageAssignment]:
        """Gets the assignments property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.assignment import (
            AccessPackageAssignment,
        )

        return self.properties.get(
            "assignments",
            EntityCollection[AccessPackageAssignment](
                self.context, AccessPackageAssignment, ResourcePath("assignments", self.resource_path)
            ),
        )

    @property
    def available_access_packages(self) -> EntityCollection[AvailableAccessPackage]:
        """Gets the availableAccessPackages property"""
        from office365.directory.identitygovernance.entitlementmanagement.available_access_package import (
            AvailableAccessPackage,
        )

        return self.properties.get(
            "availableAccessPackages",
            EntityCollection[AvailableAccessPackage](
                self.context, AvailableAccessPackage, ResourcePath("availableAccessPackages", self.resource_path)
            ),
        )

    @property
    def connected_organizations(self) -> EntityCollection[ConnectedOrganization]:
        """Gets the connectedOrganizations property"""
        from office365.directory.identitygovernance.entitlementmanagement.connected_organization import (
            ConnectedOrganization,
        )

        return self.properties.get(
            "connectedOrganizations",
            EntityCollection[ConnectedOrganization](
                self.context, ConnectedOrganization, ResourcePath("connectedOrganizations", self.resource_path)
            ),
        )

    @property
    def control_configurations(self) -> EntityCollection[ControlConfiguration]:
        """Gets the controlConfigurations property"""
        from office365.directory.identitygovernance.entitlementmanagement.control_configuration import (
            ControlConfiguration,
        )

        return self.properties.get(
            "controlConfigurations",
            EntityCollection[ControlConfiguration](
                self.context, ControlConfiguration, ResourcePath("controlConfigurations", self.resource_path)
            ),
        )

    @property
    def external_origin_resource_connectors(self) -> EntityCollection[ExternalOriginResourceConnector]:
        """Gets the externalOriginResourceConnectors property"""
        from office365.directory.identitygovernance.entitlementmanagement.external_origin_resource_connector import (
            ExternalOriginResourceConnector,
        )

        return self.properties.get(
            "externalOriginResourceConnectors",
            EntityCollection[ExternalOriginResourceConnector](
                self.context,
                ExternalOriginResourceConnector,
                ResourcePath("externalOriginResourceConnectors", self.resource_path),
            ),
        )

    @property
    def resource_environments(self) -> EntityCollection[AccessPackageResourceEnvironment]:
        """Gets the resourceEnvironments property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_environment import (
            AccessPackageResourceEnvironment,
        )

        return self.properties.get(
            "resourceEnvironments",
            EntityCollection[AccessPackageResourceEnvironment](
                self.context, AccessPackageResourceEnvironment, ResourcePath("resourceEnvironments", self.resource_path)
            ),
        )

    @property
    def resource_role_scopes(self) -> EntityCollection[AccessPackageResourceRoleScope]:
        """Gets the resourceRoleScopes property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_role_scope import (
            AccessPackageResourceRoleScope,
        )

        return self.properties.get(
            "resourceRoleScopes",
            EntityCollection[AccessPackageResourceRoleScope](
                self.context, AccessPackageResourceRoleScope, ResourcePath("resourceRoleScopes", self.resource_path)
            ),
        )

    @property
    def resources(self) -> EntityCollection[AccessPackageResource]:
        """Gets the resources property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource import (
            AccessPackageResource,
        )

        return self.properties.get(
            "resources",
            EntityCollection[AccessPackageResource](
                self.context, AccessPackageResource, ResourcePath("resources", self.resource_path)
            ),
        )

    @property
    def settings(self) -> EntitlementManagementSettings:
        """Gets the settings property"""
        from office365.directory.identitygovernance.entitlementmanagement.management_settings import (
            EntitlementManagementSettings,
        )

        return self.properties.get(
            "settings", EntitlementManagementSettings(self.context, ResourcePath("settings", self.resource_path))
        )

    @property
    def subjects(self) -> EntityCollection[AccessPackageSubject]:
        """Gets the subjects property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.subject import (
            AccessPackageSubject,
        )

        return self.properties.get(
            "subjects",
            EntityCollection[AccessPackageSubject](
                self.context, AccessPackageSubject, ResourcePath("subjects", self.resource_path)
            ),
        )
