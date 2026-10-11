from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.identitygovernance.entitlementmanagement.accesspackage.catalogstate import (
    AccessPackageCatalogState,
)
from office365.directory.identitygovernance.entitlementmanagement.accesspackage.catalogtype import (
    AccessPackageCatalogType,
)
from office365.directory.identitygovernance.workflow.custom_callout_extension import (
    CustomCalloutExtension,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.package import (
        AccessPackage,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource import (
        AccessPackageResource,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_role import (
        AccessPackageResourceRole,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_scope import (
        AccessPackageResourceScope,
    )


class AccessPackageCatalog(Entity):
    """In Microsoft Entra entitlement management, an access package catalog is a container for zero or more access
    packages. Microsoft Entra entitlement management includes a built-in catalog named General.

     An access package catalog might also have linked resources that are used in those access packages
     to provide access. To view or change the membership of catalog-scoped roles, use the role assignments API
     with the entitlement management RBAC provider."""

    @property
    def catalog_type(self) -> AccessPackageCatalogType:
        """Gets the catalogType property"""
        return self.properties.get("catalogType", AccessPackageCatalogType.userManaged)

    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def is_externally_visible(self) -> Optional[bool]:
        """Gets the isExternallyVisible property"""
        return self.properties.get("isExternallyVisible", None)

    @property
    def modified_date_time(self) -> datetime:
        """Gets the modifiedDateTime property"""
        return self.properties.get("modifiedDateTime", datetime.min)

    @property
    def state(self) -> AccessPackageCatalogState:
        """Gets the state property"""
        return self.properties.get("state", AccessPackageCatalogState.unpublished)

    @property
    def custom_workflow_extensions(self) -> EntityCollection[CustomCalloutExtension]:
        """Gets the customWorkflowExtensions property"""
        return self.properties.get(
            "customWorkflowExtensions",
            EntityCollection[CustomCalloutExtension](
                self.context, CustomCalloutExtension, ResourcePath("customWorkflowExtensions", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessPackageCatalog"

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
    def resource_roles(self) -> EntityCollection[AccessPackageResourceRole]:
        """Gets the resourceRoles property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_role import (
            AccessPackageResourceRole,
        )

        return self.properties.get(
            "resourceRoles",
            EntityCollection[AccessPackageResourceRole](
                self.context, AccessPackageResourceRole, ResourcePath("resourceRoles", self.resource_path)
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
    def resource_scopes(self) -> EntityCollection[AccessPackageResourceScope]:
        """Gets the resourceScopes property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_scope import (
            AccessPackageResourceScope,
        )

        return self.properties.get(
            "resourceScopes",
            EntityCollection[AccessPackageResourceScope](
                self.context, AccessPackageResourceScope, ResourcePath("resourceScopes", self.resource_path)
            ),
        )
