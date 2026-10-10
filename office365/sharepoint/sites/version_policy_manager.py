from __future__ import annotations

from typing import Optional

from typing_extensions import Self

from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata
from office365.sharepoint.entity import Entity
from office365.sharepoint.lists.version_policy_manager import VersionPolicyManager


class SiteVersionPolicyManager(Entity):
    """Manages versioning policies for a SharePoint site collection.

    Provides functionality to control document versioning settings including
    major version limits and automatic expiration policies.
    """

    @property
    def major_version_limit(self) -> Optional[int]:
        """Gets the maximum number of major versions allowed for documents.

        Returns:
            Optional[int]: The maximum number of major versions, or None if not set.
        """
        return self.properties.get("MajorVersionLimit", None)

    @odata(name="VersionPolicies")
    @property
    def version_policies(self) -> VersionPolicyManager:
        """Gets the version policies manager for detailed version control settings.

        Returns:
            VersionPolicyManager: The version policies manager instance.
        """
        return self.properties.get(
            "VersionPolicies",
            VersionPolicyManager(self.context, ResourcePath("VersionPolicies", self.resource_path)),
        )

    def inherit_tenant_settings(self) -> Self:
        """Inherits version policy settings from the tenant-level configuration.

        Applies the tenant-wide version policy settings to this site collection,
        overriding any site-specific configurations.

        Returns:
            SiteVersionPolicyManager: The version policy manager instance
        """
        qry = ServiceOperationQuery(self, "InheritTenantSettings")
        self.context.add_query(qry)
        return self

    def set_auto_expiration(self) -> Self:
        """Enables automatic expiration of document versions based on policy rules.

        Configures the site to automatically delete old document versions according
        to the established expiration policies and retention rules.

        Returns:
            SiteVersionPolicyManager: The version policy manager instance
        """
        qry = ServiceOperationQuery(self, "SetAutoExpiration")
        self.context.add_query(qry)
        return self

    def set_expire_after(self, major_version_limit: int, expire_after_days: int) -> Self:
        """SetExpireAfter operation.

        Args:
            major_version_limit (int):
                majorVersionLimit parameter
            expire_after_days (int):
                expireAfterDays parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetExpireAfter",
            None,
            {"majorVersionLimit": major_version_limit, "expireAfterDays": expire_after_days},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_no_expiration(self, major_version_limit: int) -> Self:
        """SetNoExpiration operation.

        Args:
            major_version_limit (int):
                majorVersionLimit parameter
        """
        qry = ServiceOperationQuery(
            self, "SetNoExpiration", None, {"majorVersionLimit": major_version_limit}, None, None
        )
        self.context.add_query(qry)
        return self
