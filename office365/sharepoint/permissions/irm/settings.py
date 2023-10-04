import datetime

from office365.sharepoint.base_entity import BaseEntity


class InformationRightsManagementSettings(BaseEntity):
    """Represents the Information Rights Management (IRM) settings of a list in Microsoft SharePoint Foundation."""

    @property
    def allow_print(self):
        """
        Specifies whether a user can print the downloaded document.
        :rtype: bool or None
        """
        return self.properties.get("AllowPrint", None)

    @property
    def allow_script(self):
        """
        Specifies whether a user can run scripts on the downloaded document.
        :rtype: bool or None
        """
        return self.properties.get("AllowScript", None)

    @property
    def allow_write_copy(self):
        """
        Specifies whether a user can write in a copy of the downloaded document.
        :rtype: bool or None
        """
        return self.properties.get("AllowWriteCopy", None)

    @property
    def disable_document_browser_view(self):
        """
        Specifies whether a user can write in a copy of the downloaded document.
        :rtype: bool or None
        """
        return self.properties.get("DisableDocumentBrowserView", None)

    @property
    def document_access_expire_days(self):
        """
        Specifies the number of days after which the downloaded document will expire.
        :rtype: int or None
        """
        return self.properties.get("DocumentAccessExpireDays", None)

    @property
    def document_library_protection_expire_date(self):
        """
        Specifies the date on which the Information Rights Management (IRM) protection of this document library will
        stop.
        """
        return self.properties.get(
            "DocumentLibraryProtectionExpireDate", datetime.datetime.min
        )

    @property
    def enable_document_access_expire(self):
        """
        Specifies whether the downloaded document will expire.
        :rtype: int or None
        """
        return self.properties.get("EnableDocumentAccessExpire", None)

    @property
    def enable_group_protection(self):
        """
        Specifies whether the permission of the downloaded document is applicable to a group.
        :rtype: int or None
        """
        return self.properties.get("EnableGroupProtection", None)

    @property
    def enable_license_cache_expire(self):
        """
        Specifies whether a user MUST verify his or her credentials after certain intervals.
        :rtype: int or None
        """
        return self.properties.get("EnableLicenseCacheExpire", None)

    @property
    def policy_title(self):
        """
        Specifies the permission policy title.
        :rtype: str or None
        """
        return self.properties.get("PolicyTitle", None)

    @property
    def policy_description(self):
        """
        Specifies the permission policy description.
        :rtype: str or None
        """
        return self.properties.get("PolicyDescription", None)

    @property
    def group_name(self):
        """
        Specifies the group name (email address) that the permission is also applicable to.
        :rtype: str or None
        """
        return self.properties.get("GroupName", None)

    @property
    def license_cache_expire_days(self):
        """
        Specifies the number of days that the Information Rights Management (IRM) license can be cached by the
        application to open the downloaded document. When these elapse, the application will connect to the IRM
        server to validate the license.
        :rtype: int or None
        """
        return self.properties.get("LicenseCacheExpireDays", None)

    @property
    def template_id(self):
        """
        Gets or sets the ID of the RMS template that will be applied to the file or library.
        :rtype: str or None
        """
        return self.properties.get("TemplateId", None)
