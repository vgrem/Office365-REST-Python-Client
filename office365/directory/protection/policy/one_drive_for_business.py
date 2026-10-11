from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.protection.policy.base import ProtectionPolicyBase
from office365.directory.protection.rules.drive import DriveProtectionRule
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.drive_protection_unit import DriveProtectionUnit
    from office365.common.drive_protection_units_bulk_addition_job import (
        DriveProtectionUnitsBulkAdditionJob,
    )


class OneDriveForBusinessProtectionPolicy(ProtectionPolicyBase):
    """
    Contains details about protection policies applied to Microsoft 365 data in an organization.
    Protection policies are defined by the Global Admin (or the SharePoint Online Admin or Exchange Online Admin)
    and include what data to protect, when to protect it, and for what time period to retain the protected data
    for a single Microsoft 365 service.
    """

    @property
    def drive_inclusion_rules(self) -> EntityCollection[DriveProtectionRule]:
        """Contains the details of the Onedrive for Business protection rule."""
        return self.properties.get(
            "driveInclusionRules",
            EntityCollection(
                self.context,
                DriveProtectionRule,
                ResourcePath("driveInclusionRules", self.resource_path),
            ),
        )

    @property
    def drive_protection_units(self) -> EntityCollection[DriveProtectionUnit]:
        """Gets the driveProtectionUnits property"""
        from office365.common.drive_protection_unit import DriveProtectionUnit

        return self.properties.get(
            "driveProtectionUnits",
            EntityCollection[DriveProtectionUnit](
                self.context, DriveProtectionUnit, ResourcePath("driveProtectionUnits", self.resource_path)
            ),
        )

    @property
    def drive_protection_units_bulk_addition_jobs(self) -> EntityCollection[DriveProtectionUnitsBulkAdditionJob]:
        """Gets the driveProtectionUnitsBulkAdditionJobs property"""
        from office365.common.drive_protection_units_bulk_addition_job import (
            DriveProtectionUnitsBulkAdditionJob,
        )

        return self.properties.get(
            "driveProtectionUnitsBulkAdditionJobs",
            EntityCollection[DriveProtectionUnitsBulkAdditionJob](
                self.context,
                DriveProtectionUnitsBulkAdditionJob,
                ResourcePath("driveProtectionUnitsBulkAdditionJobs", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OneDriveForBusinessProtectionPolicy"
