from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.objects.collection import DirectoryObjectCollection
from office365.directory.objects.object import DirectoryObject
from office365.entity_collection import EntityCollection
from office365.intune.devices.alternative_security_id import AlternativeSecurityId
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.extensions.extension import Extension


class Device(DirectoryObject):
    """
    Represents a device registered in the organization. Devices are created in the cloud using the
    Device Registration Service or by Intune. They're used by conditional access policies for multi-factor
    authentication. These devices can range from desktop and laptop machines to phones and tablets.
    """

    def __repr__(self):
        return self.device_id or self.entity_type_name

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Device"

    @property
    def account_enabled(self) -> Optional[bool]:
        """true if the account is enabled; otherwise, false. Required. Default is true.

        Supports $filter (eq, ne, not, in). Only callers with at least the Cloud Device Administrator
        role can set this property."""
        return self.properties.get("accountEnabled", None)

    @odata(name="alternativeSecurityIds")
    @property
    def alternative_security_ids(self) -> ClientValueCollection[AlternativeSecurityId]:
        """For internal use only."""
        return self.properties.get("alternativeSecurityIds", ClientValueCollection(AlternativeSecurityId))

    @odata(name="approximateLastSignInDateTime")
    @property
    def approximate_last_signin_datetime(self) -> datetime:
        """The timestamp type represents date and time information using ISO 8601 format and is always in UTC time.
        For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Read-only.
        Supports $filter (eq, ne, not, ge, le, and eq on null values) and $orderby."""
        return self.properties.get("approximateLastSignInDateTime", datetime.min)

    @odata(name="complianceExpirationDateTime")
    @property
    def compliance_expiration_datetime(self) -> datetime:
        """The timestamp when the device is no longer deemed compliant. The timestamp type represents date and
        time information using ISO 8601 format and is always in UTC time.
        For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Read-only."""
        return self.properties.get("complianceExpirationDateTime", datetime.min)

    @property
    def device_id(self) -> Optional[str]:
        """Unique identifier set by Azure Device Registration Service at the time of registration.
        This is an alternate key that can be used to reference the device object."""
        return self.properties.get("deviceId", None)

    @property
    def device_ownership(self) -> Optional[str]:
        """Ownership of the device. This property is set by Intune. Possible values are: unknown, company, personal."""
        return self.properties.get("deviceOwnership", None)

    @odata(name="memberOf")
    @property
    def member_of(self) -> DirectoryObjectCollection:
        """Groups and administrative units that this device is a member of."""
        return self.properties.get(
            "memberOf",
            DirectoryObjectCollection(self.context, ResourcePath("memberOf", self.resource_path)),
        )

    @odata(name="registeredOwners")
    @property
    def registered_owners(self) -> DirectoryObjectCollection:
        """The user that cloud joined the device or registered their personal device.
        The registered owner is set at the time of registration. Currently, there can be only one owner.
        """
        return self.properties.get(
            "registeredOwners",
            DirectoryObjectCollection(self.context, ResourcePath("registeredOwners", self.resource_path)),
        )

    @odata(name="registeredUsers")
    @property
    def registered_users(self) -> DirectoryObjectCollection:
        """Collection of registered users of the device. For cloud joined devices and registered personal devices,
        registered users are set to the same value as registered owners at the time of registration.
        """
        return self.properties.get(
            "registeredUsers",
            DirectoryObjectCollection(self.context, ResourcePath("registeredUsers", self.resource_path)),
        )

    @odata(name="transitiveMemberOf")
    @property
    def transitive_member_of(self) -> DirectoryObjectCollection:
        """Get groups, directory roles that the user is a member of. This API request is transitive, and will also
        return all groups the user is a nested member of."""
        return self.properties.get(
            "transitiveMemberOf",
            DirectoryObjectCollection(self.context, ResourcePath("transitiveMemberOf", self.resource_path)),
        )

    @property
    def device_category(self) -> Optional[str]:
        """Gets the deviceCategory property"""
        return self.properties.get("deviceCategory", None)

    @property
    def device_metadata(self) -> Optional[str]:
        """Gets the deviceMetadata property"""
        return self.properties.get("deviceMetadata", None)

    @property
    def device_version(self) -> Optional[int]:
        """Gets the deviceVersion property"""
        return self.properties.get("deviceVersion", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def enrollment_profile_name(self) -> Optional[str]:
        """Gets the enrollmentProfileName property"""
        return self.properties.get("enrollmentProfileName", None)

    @property
    def enrollment_type(self) -> Optional[str]:
        """Gets the enrollmentType property"""
        return self.properties.get("enrollmentType", None)

    @property
    def is_compliant(self) -> Optional[bool]:
        """Gets the isCompliant property"""
        return self.properties.get("isCompliant", None)

    @property
    def is_managed(self) -> Optional[bool]:
        """Gets the isManaged property"""
        return self.properties.get("isManaged", None)

    @property
    def is_management_restricted(self) -> Optional[bool]:
        """Gets the isManagementRestricted property"""
        return self.properties.get("isManagementRestricted", None)

    @property
    def is_rooted(self) -> Optional[bool]:
        """Gets the isRooted property"""
        return self.properties.get("isRooted", None)

    @property
    def management_type(self) -> Optional[str]:
        """Gets the managementType property"""
        return self.properties.get("managementType", None)

    @property
    def manufacturer(self) -> Optional[str]:
        """Gets the manufacturer property"""
        return self.properties.get("manufacturer", None)

    @property
    def mdm_app_id(self) -> Optional[str]:
        """Gets the mdmAppId property"""
        return self.properties.get("mdmAppId", None)

    @property
    def model(self) -> Optional[str]:
        """Gets the model property"""
        return self.properties.get("model", None)

    @property
    def on_premises_last_sync_date_time(self) -> Optional[datetime]:
        """Gets the onPremisesLastSyncDateTime property"""
        return self.properties.get("onPremisesLastSyncDateTime", datetime.min)

    @property
    def on_premises_security_identifier(self) -> Optional[str]:
        """Gets the onPremisesSecurityIdentifier property"""
        return self.properties.get("onPremisesSecurityIdentifier", None)

    @property
    def on_premises_sync_enabled(self) -> Optional[bool]:
        """Gets the onPremisesSyncEnabled property"""
        return self.properties.get("onPremisesSyncEnabled", None)

    @property
    def operating_system(self) -> Optional[str]:
        """Gets the operatingSystem property"""
        return self.properties.get("operatingSystem", None)

    @property
    def operating_system_version(self) -> Optional[str]:
        """Gets the operatingSystemVersion property"""
        return self.properties.get("operatingSystemVersion", None)

    @property
    def physical_ids(self) -> StringCollection:
        """Gets the physicalIds property"""
        return self.properties.get("physicalIds", StringCollection())

    @property
    def profile_type(self) -> Optional[str]:
        """Gets the profileType property"""
        return self.properties.get("profileType", None)

    @property
    def registration_date_time(self) -> Optional[datetime]:
        """Gets the registrationDateTime property"""
        return self.properties.get("registrationDateTime", datetime.min)

    @property
    def system_labels(self) -> StringCollection:
        """Gets the systemLabels property"""
        return self.properties.get("systemLabels", StringCollection())

    @property
    def trust_type(self) -> Optional[str]:
        """Gets the trustType property"""
        return self.properties.get("trustType", None)

    @property
    def extensions(self) -> EntityCollection[Extension]:
        """Gets the extensions property"""
        from office365.directory.extensions.extension import Extension

        return self.properties.get(
            "extensions",
            EntityCollection[Extension](self.context, Extension, ResourcePath("extensions", self.resource_path)),
        )
