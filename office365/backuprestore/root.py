from __future__ import annotations

from typing import TYPE_CHECKING

from office365.backuprestore.service_status import ServiceStatus
from office365.directory.permissions.require_permission import require_permission
from office365.directory.protection.policy.one_drive_for_business import (
    OneDriveForBusinessProtectionPolicy,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.backuprestore.browse_session_base import BrowseSessionBase
    from office365.backuprestore.email_notifications_setting import (
        EmailNotificationsSetting,
    )
    from office365.backuprestore.onedrive_for_business_browse_session import (
        OneDriveForBusinessBrowseSession,
    )
    from office365.backuprestore.onedrive_for_business_restore_session import (
        OneDriveForBusinessRestoreSession,
    )
    from office365.backuprestore.protection_unit_base import ProtectionUnitBase
    from office365.backuprestore.restorepoints.collection import RestorePointCollection
    from office365.backuprestore.serviceapps.service_app import ServiceApp
    from office365.backuprestore.sharepoint_browse_session import (
        SharePointBrowseSession,
    )
    from office365.backuprestore.sharepoint_protection_policy import (
        SharePointProtectionPolicy,
    )
    from office365.backuprestore.sharepoint_restore_session import (
        SharePointRestoreSession,
    )
    from office365.common.drive_protection_unit import DriveProtectionUnit
    from office365.common.drive_protection_units_bulk_addition_job import (
        DriveProtectionUnitsBulkAdditionJob,
    )
    from office365.common.exchange_protection_policy import ExchangeProtectionPolicy
    from office365.common.exchange_restore_session import ExchangeRestoreSession
    from office365.common.mailbox_protection_rule import MailboxProtectionRule
    from office365.common.mailbox_protection_unit import MailboxProtectionUnit
    from office365.common.mailbox_protection_units_bulk_addition_job import (
        MailboxProtectionUnitsBulkAdditionJob,
    )
    from office365.common.restore_session_base import RestoreSessionBase
    from office365.common.site_protection_rule import SiteProtectionRule
    from office365.common.site_protection_unit import SiteProtectionUnit
    from office365.common.site_protection_units_bulk_addition_job import (
        SiteProtectionUnitsBulkAdditionJob,
    )
    from office365.directory.protection.policy.base import ProtectionPolicyBase
    from office365.directory.protection.rules.drive import DriveProtectionRule


class BackupRestoreRoot(Entity):
    """Represents the Microsoft 365 Backup Storage service in a tenant."""

    @require_permission(
        delegated=["BackupRestore-Control.ReadWrite.All"],
        application=["BackupRestore-Control.ReadWrite.All"],
    )
    def enable(self, app_owner_tenant_id: str) -> ClientResult[ServiceStatus]:
        """Enable the Microsoft 365 Backup Storage service for a tenant."""
        return_type = ClientResult(self.context, ServiceStatus())
        payload = {"appOwnerTenantId": app_owner_tenant_id}
        qry = ServiceOperationQuery(self, "enable", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @odata(name="serviceStatus")
    @property
    def service_status(self) -> ServiceStatus:
        """Represents the tenant-level status of the Backup Storage service."""
        return self.properties.get("serviceStatus", ServiceStatus())

    @odata(name="oneDriveForBusinessProtectionPolicies")
    @property
    def one_drive_for_business_protection_policies(
        self,
    ) -> EntityCollection[OneDriveForBusinessProtectionPolicy]:
        """The list of OneDrive for Business restore sessions available in the tenant."""
        return self.properties.get(
            "oneDriveForBusinessProtectionPolicies",
            EntityCollection(
                self.context,
                OneDriveForBusinessProtectionPolicy,
                ResourcePath("oneDriveForBusinessProtectionPolicies", self.resource_path),
            ),
        )

    @property
    def browse_sessions(self) -> EntityCollection[BrowseSessionBase]:
        """Gets the browseSessions property"""
        from office365.backuprestore.browse_session_base import BrowseSessionBase

        return self.properties.get(
            "browseSessions",
            EntityCollection[BrowseSessionBase](
                self.context, BrowseSessionBase, ResourcePath("browseSessions", self.resource_path)
            ),
        )

    @property
    def drive_inclusion_rules(self) -> EntityCollection[DriveProtectionRule]:
        """Gets the driveInclusionRules property"""
        from office365.directory.protection.rules.drive import DriveProtectionRule

        return self.properties.get(
            "driveInclusionRules",
            EntityCollection[DriveProtectionRule](
                self.context, DriveProtectionRule, ResourcePath("driveInclusionRules", self.resource_path)
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
    def email_notifications_setting(self) -> EmailNotificationsSetting:
        """Gets the emailNotificationsSetting property"""
        from office365.backuprestore.email_notifications_setting import (
            EmailNotificationsSetting,
        )

        return self.properties.get(
            "emailNotificationsSetting",
            EmailNotificationsSetting(self.context, ResourcePath("emailNotificationsSetting", self.resource_path)),
        )

    @property
    def exchange_protection_policies(self) -> EntityCollection[ExchangeProtectionPolicy]:
        """Gets the exchangeProtectionPolicies property"""
        from office365.common.exchange_protection_policy import ExchangeProtectionPolicy

        return self.properties.get(
            "exchangeProtectionPolicies",
            EntityCollection[ExchangeProtectionPolicy](
                self.context, ExchangeProtectionPolicy, ResourcePath("exchangeProtectionPolicies", self.resource_path)
            ),
        )

    @property
    def exchange_restore_sessions(self) -> EntityCollection[ExchangeRestoreSession]:
        """Gets the exchangeRestoreSessions property"""
        from office365.common.exchange_restore_session import ExchangeRestoreSession

        return self.properties.get(
            "exchangeRestoreSessions",
            EntityCollection[ExchangeRestoreSession](
                self.context, ExchangeRestoreSession, ResourcePath("exchangeRestoreSessions", self.resource_path)
            ),
        )

    @property
    def mailbox_inclusion_rules(self) -> EntityCollection[MailboxProtectionRule]:
        """Gets the mailboxInclusionRules property"""
        from office365.common.mailbox_protection_rule import MailboxProtectionRule

        return self.properties.get(
            "mailboxInclusionRules",
            EntityCollection[MailboxProtectionRule](
                self.context, MailboxProtectionRule, ResourcePath("mailboxInclusionRules", self.resource_path)
            ),
        )

    @property
    def mailbox_protection_units(self) -> EntityCollection[MailboxProtectionUnit]:
        """Gets the mailboxProtectionUnits property"""
        from office365.common.mailbox_protection_unit import MailboxProtectionUnit

        return self.properties.get(
            "mailboxProtectionUnits",
            EntityCollection[MailboxProtectionUnit](
                self.context, MailboxProtectionUnit, ResourcePath("mailboxProtectionUnits", self.resource_path)
            ),
        )

    @property
    def mailbox_protection_units_bulk_addition_jobs(self) -> EntityCollection[MailboxProtectionUnitsBulkAdditionJob]:
        """Gets the mailboxProtectionUnitsBulkAdditionJobs property"""
        from office365.common.mailbox_protection_units_bulk_addition_job import (
            MailboxProtectionUnitsBulkAdditionJob,
        )

        return self.properties.get(
            "mailboxProtectionUnitsBulkAdditionJobs",
            EntityCollection[MailboxProtectionUnitsBulkAdditionJob](
                self.context,
                MailboxProtectionUnitsBulkAdditionJob,
                ResourcePath("mailboxProtectionUnitsBulkAdditionJobs", self.resource_path),
            ),
        )

    @property
    def onedrive_for_business_browse_sessions(self) -> EntityCollection[OneDriveForBusinessBrowseSession]:
        """Gets the oneDriveForBusinessBrowseSessions property"""
        from office365.backuprestore.onedrive_for_business_browse_session import (
            OneDriveForBusinessBrowseSession,
        )

        return self.properties.get(
            "oneDriveForBusinessBrowseSessions",
            EntityCollection[OneDriveForBusinessBrowseSession](
                self.context,
                OneDriveForBusinessBrowseSession,
                ResourcePath("oneDriveForBusinessBrowseSessions", self.resource_path),
            ),
        )

    @property
    def onedrive_for_business_restore_sessions(self) -> EntityCollection[OneDriveForBusinessRestoreSession]:
        """Gets the oneDriveForBusinessRestoreSessions property"""
        from office365.backuprestore.onedrive_for_business_restore_session import (
            OneDriveForBusinessRestoreSession,
        )

        return self.properties.get(
            "oneDriveForBusinessRestoreSessions",
            EntityCollection[OneDriveForBusinessRestoreSession](
                self.context,
                OneDriveForBusinessRestoreSession,
                ResourcePath("oneDriveForBusinessRestoreSessions", self.resource_path),
            ),
        )

    @property
    def protection_policies(self) -> EntityCollection[ProtectionPolicyBase]:
        """Gets the protectionPolicies property"""
        from office365.directory.protection.policy.base import ProtectionPolicyBase

        return self.properties.get(
            "protectionPolicies",
            EntityCollection[ProtectionPolicyBase](
                self.context, ProtectionPolicyBase, ResourcePath("protectionPolicies", self.resource_path)
            ),
        )

    @property
    def protection_units(self) -> EntityCollection[ProtectionUnitBase]:
        """Gets the protectionUnits property"""
        from office365.backuprestore.protection_unit_base import ProtectionUnitBase

        return self.properties.get(
            "protectionUnits",
            EntityCollection[ProtectionUnitBase](
                self.context, ProtectionUnitBase, ResourcePath("protectionUnits", self.resource_path)
            ),
        )

    @property
    def restore_points(self) -> RestorePointCollection:
        """Gets the restorePoints property"""
        from office365.backuprestore.restorepoints.collection import (
            RestorePointCollection,
        )
        from office365.common.restore_point import RestorePoint

        return self.properties.get(
            "restorePoints",
            RestorePointCollection(self.context, RestorePoint, ResourcePath("restorePoints", self.resource_path)),
        )

    @property
    def restore_sessions(self) -> EntityCollection[RestoreSessionBase]:
        """Gets the restoreSessions property"""
        from office365.common.restore_session_base import RestoreSessionBase

        return self.properties.get(
            "restoreSessions",
            EntityCollection[RestoreSessionBase](
                self.context, RestoreSessionBase, ResourcePath("restoreSessions", self.resource_path)
            ),
        )

    @property
    def service_apps(self) -> EntityCollection[ServiceApp]:
        """Gets the serviceApps property"""
        from office365.backuprestore.serviceapps.service_app import ServiceApp

        return self.properties.get(
            "serviceApps",
            EntityCollection[ServiceApp](self.context, ServiceApp, ResourcePath("serviceApps", self.resource_path)),
        )

    @property
    def sharepoint_browse_sessions(self) -> EntityCollection[SharePointBrowseSession]:
        """Gets the sharePointBrowseSessions property"""
        from office365.backuprestore.sharepoint_browse_session import (
            SharePointBrowseSession,
        )

        return self.properties.get(
            "sharePointBrowseSessions",
            EntityCollection[SharePointBrowseSession](
                self.context, SharePointBrowseSession, ResourcePath("sharePointBrowseSessions", self.resource_path)
            ),
        )

    @property
    def sharepoint_protection_policies(self) -> EntityCollection[SharePointProtectionPolicy]:
        """Gets the sharePointProtectionPolicies property"""
        from office365.backuprestore.sharepoint_protection_policy import (
            SharePointProtectionPolicy,
        )

        return self.properties.get(
            "sharePointProtectionPolicies",
            EntityCollection[SharePointProtectionPolicy](
                self.context,
                SharePointProtectionPolicy,
                ResourcePath("sharePointProtectionPolicies", self.resource_path),
            ),
        )

    @property
    def sharepoint_restore_sessions(self) -> EntityCollection[SharePointRestoreSession]:
        """Gets the sharePointRestoreSessions property"""
        from office365.backuprestore.sharepoint_restore_session import (
            SharePointRestoreSession,
        )

        return self.properties.get(
            "sharePointRestoreSessions",
            EntityCollection[SharePointRestoreSession](
                self.context, SharePointRestoreSession, ResourcePath("sharePointRestoreSessions", self.resource_path)
            ),
        )

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
        return "microsoft.graph.BackupRestoreRoot"
