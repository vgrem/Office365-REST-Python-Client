from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.groups.group import Group
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.assignment_policy import (
        AccessPackageAssignmentPolicy,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.catalog import (
        AccessPackageCatalog,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_role_scope import (
        AccessPackageResourceRoleScope,
    )


class AccessPackage(Entity):
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
    def is_hidden(self) -> Optional[bool]:
        """Gets the isHidden property"""
        return self.properties.get("isHidden", None)

    @property
    def modified_date_time(self) -> datetime:
        """Gets the modifiedDateTime property"""
        return self.properties.get("modifiedDateTime", datetime.min)

    @property
    def access_packages_incompatible_with(self) -> EntityCollection[AccessPackage]:
        """Gets the accessPackagesIncompatibleWith property"""
        return self.properties.get(
            "accessPackagesIncompatibleWith",
            EntityCollection[AccessPackage](
                self.context, AccessPackage, ResourcePath("accessPackagesIncompatibleWith", self.resource_path)
            ),
        )

    @property
    def incompatible_access_packages(self) -> EntityCollection[AccessPackage]:
        """Gets the incompatibleAccessPackages property"""
        return self.properties.get(
            "incompatibleAccessPackages",
            EntityCollection[AccessPackage](
                self.context, AccessPackage, ResourcePath("incompatibleAccessPackages", self.resource_path)
            ),
        )

    @property
    def incompatible_groups(self) -> EntityCollection[Group]:
        """Gets the incompatibleGroups property"""
        return self.properties.get(
            "incompatibleGroups",
            EntityCollection[Group](self.context, Group, ResourcePath("incompatibleGroups", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessPackage"

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
    def catalog(self) -> AccessPackageCatalog:
        """Gets the catalog property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.catalog import (
            AccessPackageCatalog,
        )

        return self.properties.get(
            "catalog", AccessPackageCatalog(self.context, ResourcePath("catalog", self.resource_path))
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
