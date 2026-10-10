from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.sharepoint.entity import Entity


class EffectiveInformationRightsManagementSettings(Entity):
    """A collection of effective IRM settings on the file."""

    @property
    def allow_print(self) -> Optional[bool]:
        """Specifies whether a user can print the downloaded document."""
        return self.properties.get("AllowPrint", None)

    @property
    def template_id(self) -> Optional[str]:
        """Gets the template ID of the RMS template that will be applied to the file/library."""
        return self.properties.get("TemplateId", None)

    @property
    def allow_script(self) -> Optional[bool]:
        """Gets the AllowScript property"""
        return self.properties.get("AllowScript", None)

    @property
    def allow_write_copy(self) -> Optional[bool]:
        """Gets the AllowWriteCopy property"""
        return self.properties.get("AllowWriteCopy", None)

    @property
    def disable_document_browser_view(self) -> Optional[bool]:
        """Gets the DisableDocumentBrowserView property"""
        return self.properties.get("DisableDocumentBrowserView", None)

    @property
    def document_access_expire_days(self) -> Optional[int]:
        """Gets the DocumentAccessExpireDays property"""
        return self.properties.get("DocumentAccessExpireDays", None)

    @property
    def document_library_protection_expire_date(self) -> Optional[datetime]:
        """Gets the DocumentLibraryProtectionExpireDate property"""
        return self.properties.get("DocumentLibraryProtectionExpireDate", datetime.min)

    @property
    def enable_document_access_expire(self) -> Optional[bool]:
        """Gets the EnableDocumentAccessExpire property"""
        return self.properties.get("EnableDocumentAccessExpire", None)

    @property
    def enable_document_browser_publishing_view(self) -> Optional[bool]:
        """Gets the EnableDocumentBrowserPublishingView property"""
        return self.properties.get("EnableDocumentBrowserPublishingView", None)

    @property
    def enable_group_protection(self) -> Optional[bool]:
        """Gets the EnableGroupProtection property"""
        return self.properties.get("EnableGroupProtection", None)

    @property
    def enable_license_cache_expire(self) -> Optional[bool]:
        """Gets the EnableLicenseCacheExpire property"""
        return self.properties.get("EnableLicenseCacheExpire", None)

    @property
    def group_name(self) -> Optional[str]:
        """Gets the GroupName property"""
        return self.properties.get("GroupName", None)

    @property
    def irm_enabled(self) -> Optional[bool]:
        """Gets the IrmEnabled property"""
        return self.properties.get("IrmEnabled", None)

    @property
    def license_cache_expire_days(self) -> Optional[int]:
        """Gets the LicenseCacheExpireDays property"""
        return self.properties.get("LicenseCacheExpireDays", None)

    @property
    def policy_description(self) -> Optional[str]:
        """Gets the PolicyDescription property"""
        return self.properties.get("PolicyDescription", None)

    @property
    def policy_title(self) -> Optional[str]:
        """Gets the PolicyTitle property"""
        return self.properties.get("PolicyTitle", None)

    @property
    def setting_source(self) -> Optional[int]:
        """Gets the SettingSource property"""
        return self.properties.get("SettingSource", None)
