from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.certificates.auth_configuration import (
    CertificateBasedAuthConfiguration,
)
from office365.directory.domains.verified import VerifiedDomain
from office365.directory.extensions.extension import Extension
from office365.directory.licenses.assigned_plan import AssignedPlan
from office365.directory.objects.object import DirectoryObject
from office365.directory.users.provisioned_plan import ProvisionedPlan
from office365.entity_collection import EntityCollection
from office365.intune.organizations.branding import OrganizationalBranding
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.tenantinformation.partner_tenant_type import (
        PartnerTenantType,
    )
    from office365.intune.devices.mdmauthority import MdmAuthority
    from office365.intune.organizations.privacy_profile import PrivacyProfile


class Organization(DirectoryObject):
    """
    The organization resource represents an instance of global settings and resources
    which operate and are provisioned at the tenant-level.
    """

    @odata(name="assignedPlans")
    @property
    def assigned_plans(self) -> ClientValueCollection[AssignedPlan]:
        """The plans that are assigned to the organization."""
        return self.properties.get("assignedPlans", ClientValueCollection(AssignedPlan))

    @property
    def branding(self) -> OrganizationalBranding:
        return self.properties.get(
            "branding",
            OrganizationalBranding(self.context, ResourcePath("branding", self.resource_path)),
        )

    @odata(name="businessPhones")
    @property
    def business_phones(self) -> StringCollection:
        """
        Telephone number for the organization. Although this is a string collection,
        only one number can be set for this property.
        """
        return self.properties.get("businessPhones", StringCollection())

    @property
    def extensions(self) -> EntityCollection[Extension]:
        """The collection of open extensions defined for the message. Nullable."""
        return self.properties.get(
            "extensions",
            EntityCollection(self.context, Extension, ResourcePath("extensions", self.resource_path)),
        )

    @odata(name="certificateBasedAuthConfiguration")
    @property
    def certificate_based_auth_configuration(self) -> EntityCollection[CertificateBasedAuthConfiguration]:
        """Navigation property to manage certificate-based authentication configuration.
        Only a single instance of certificateBasedAuthConfiguration can be created in the collection..
        """
        return self.properties.get(
            "certificateBasedAuthConfiguration",
            EntityCollection(
                self.context,
                CertificateBasedAuthConfiguration,
                ResourcePath("certificateBasedAuthConfiguration", self.resource_path),
            ),
        )

    @odata(name="provisionedPlans")
    @property
    def provisioned_plans(self) -> ClientValueCollection[ProvisionedPlan]:
        return self.properties.get("provisionedPlans", ClientValueCollection(ProvisionedPlan))

    @odata(name="verifiedDomains")
    @property
    def verified_domains(self) -> ClientValueCollection[VerifiedDomain]:
        """The collection of domains associated with this tenant."""
        return self.properties.get("verifiedDomains", ClientValueCollection(VerifiedDomain))

    @property
    def city(self) -> Optional[str]:
        """Gets the city property"""
        return self.properties.get("city", None)

    @property
    def country(self) -> Optional[str]:
        """Gets the country property"""
        return self.properties.get("country", None)

    @property
    def country_letter_code(self) -> Optional[str]:
        """Gets the countryLetterCode property"""
        return self.properties.get("countryLetterCode", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def default_usage_location(self) -> Optional[str]:
        """Gets the defaultUsageLocation property"""
        return self.properties.get("defaultUsageLocation", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def marketing_notification_emails(self) -> StringCollection:
        """Gets the marketingNotificationEmails property"""
        return self.properties.get("marketingNotificationEmails", StringCollection())

    @property
    def on_premises_last_sync_date_time(self) -> Optional[datetime]:
        """Gets the onPremisesLastSyncDateTime property"""
        return self.properties.get("onPremisesLastSyncDateTime", datetime.min)

    @property
    def on_premises_sync_enabled(self) -> Optional[bool]:
        """Gets the onPremisesSyncEnabled property"""
        return self.properties.get("onPremisesSyncEnabled", None)

    @property
    def partner_tenant_type(self) -> PartnerTenantType:
        """Gets the partnerTenantType property"""
        from office365.directory.tenantinformation.partner_tenant_type import (
            PartnerTenantType,
        )

        return self.properties.get("partnerTenantType", PartnerTenantType.microsoftSupport)

    @property
    def postal_code(self) -> Optional[str]:
        """Gets the postalCode property"""
        return self.properties.get("postalCode", None)

    @property
    def preferred_language(self) -> Optional[str]:
        """Gets the preferredLanguage property"""
        return self.properties.get("preferredLanguage", None)

    @property
    def privacy_profile(self) -> PrivacyProfile:
        """Gets the privacyProfile property"""
        from office365.intune.organizations.privacy_profile import PrivacyProfile

        return self.properties.get("privacyProfile", PrivacyProfile())

    @property
    def security_compliance_notification_mails(self) -> StringCollection:
        """Gets the securityComplianceNotificationMails property"""
        return self.properties.get("securityComplianceNotificationMails", StringCollection())

    @property
    def security_compliance_notification_phones(self) -> StringCollection:
        """Gets the securityComplianceNotificationPhones property"""
        return self.properties.get("securityComplianceNotificationPhones", StringCollection())

    @property
    def state(self) -> Optional[str]:
        """Gets the state property"""
        return self.properties.get("state", None)

    @property
    def street(self) -> Optional[str]:
        """Gets the street property"""
        return self.properties.get("street", None)

    @property
    def technical_notification_mails(self) -> StringCollection:
        """Gets the technicalNotificationMails property"""
        return self.properties.get("technicalNotificationMails", StringCollection())

    @property
    def tenant_type(self) -> Optional[str]:
        """Gets the tenantType property"""
        return self.properties.get("tenantType", None)

    @property
    def mobile_device_management_authority(self) -> MdmAuthority:
        """Gets the mobileDeviceManagementAuthority property"""
        from office365.intune.devices.mdmauthority import MdmAuthority

        return self.properties.get("mobileDeviceManagementAuthority", MdmAuthority.unknown)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Organization"
