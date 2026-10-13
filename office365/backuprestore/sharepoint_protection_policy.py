from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.protection.policy.base import ProtectionPolicyBase
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.site_protection_rule import SiteProtectionRule
    from office365.common.site_protection_unit import SiteProtectionUnit
    from office365.common.site_protection_units_bulk_addition_job import (
        SiteProtectionUnitsBulkAdditionJob,
    )


class SharePointProtectionPolicy(ProtectionPolicyBase):
    @property
    def site_inclusion_rules(self) -> EntityCollection[SiteProtectionRule]:
        """Gets the siteInclusionRules property"""
        from office365.common.site_protection_rule import SiteProtectionRule

        return self.properties.get(
            "siteInclusionRules",
            EntityCollection[SiteProtectionRule](
                self.context, SiteProtectionRule, ResourcePath("siteInclusionRules", self.resource_path)
            ),
        )

    @property
    def site_protection_units(self) -> EntityCollection[SiteProtectionUnit]:
        """Gets the siteProtectionUnits property"""
        from office365.common.site_protection_unit import SiteProtectionUnit

        return self.properties.get(
            "siteProtectionUnits",
            EntityCollection[SiteProtectionUnit](
                self.context, SiteProtectionUnit, ResourcePath("siteProtectionUnits", self.resource_path)
            ),
        )

    @property
    def site_protection_units_bulk_addition_jobs(self) -> EntityCollection[SiteProtectionUnitsBulkAdditionJob]:
        """Gets the siteProtectionUnitsBulkAdditionJobs property"""
        from office365.common.site_protection_units_bulk_addition_job import (
            SiteProtectionUnitsBulkAdditionJob,
        )

        return self.properties.get(
            "siteProtectionUnitsBulkAdditionJobs",
            EntityCollection[SiteProtectionUnitsBulkAdditionJob](
                self.context,
                SiteProtectionUnitsBulkAdditionJob,
                ResourcePath("siteProtectionUnitsBulkAdditionJobs", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SharePointProtectionPolicy"
