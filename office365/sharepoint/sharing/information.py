from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity
from office365.sharepoint.sharing.abilities import SharingAbilities
from office365.sharepoint.sharing.access_request_settings import AccessRequestSettings
from office365.sharepoint.sharing.domain_restriction_settings import (
    DomainRestrictionSettings,
)
from office365.sharepoint.sharing.links.default_templates_collection import (
    SharingLinkDefaultTemplatesCollection,
)
from office365.sharepoint.sharing.permission_collection import PermissionCollection
from office365.sharepoint.sharing.picker_settings import PickerSettings

if TYPE_CHECKING:
    from office365.sharepoint.sharing.address_bar_link_settings import (
        AddressBarLinkSettings,
    )
    from office365.sharepoint.sharing.itemsharingsettings import ItemSharingSettings
    from office365.sharepoint.sharing.recipient_limits import RecipientLimits
    from office365.sharepoint.sharing.sensitivitylabelinformation import (
        SensitivityLabelInformation,
    )
    from office365.sharepoint.sharing.uniqueaccessgroupswrapper import (
        UniqueAccessGroupsWrapper,
    )


class SharingInformation(Entity):
    """Represents a response for Microsoft.SharePoint.Client.Sharing.SecurableObjectExtensions.GetSharingInformation.
    The accessRequestSettings, domainRestrictionSettings and permissionsInformation properties are not included in
    the default scalar property set for this type.
    """

    @property
    def access_request_settings(self):
        """
        AccessRequestSettings is an optional property set to retrieve details for pending access requests if present.
        """
        return self.properties.get("accessRequestSettings", AccessRequestSettings())

    @property
    def anonymous_link_expiration_restriction_days(self) -> Optional[int]:
        """Tenant's anonymous link expiration restriction in days."""
        return self.properties.get("anonymousLinkExpirationRestrictionDays", None)

    @property
    def domain_restriction_settings(self):
        """Whether DomainRestrictionSettings is used to limit the external Users set by Admin."""
        return self.properties.get("anonymousLinkExpirationRestrictionDays", DomainRestrictionSettings())

    @property
    def permissions_information(self):
        """
        The PermissionCollection that are on the list item. It contains a collection of PrincipalInfo and LinkInfo.
        """
        return self.properties.get("permissionsInformation", PermissionCollection())

    @property
    def picker_settings(self):
        """PickerSettings used by the PeoplePicker Control."""
        return self.properties.get(
            "pickerSettings",
            PickerSettings(self.context, ResourcePath("pickerSettings", self.resource_path)),
        )

    @property
    def sharing_abilities(self):
        """
        Matrix of possible sharing abilities per sharing type and the state of each capability for the current user
        on the list item."""
        return self.properties.get("sharingAbilities", SharingAbilities())

    @property
    def sharing_link_templates(self):
        """"""
        return self.properties.get("sharingLinkTemplates", SharingLinkDefaultTemplatesCollection())

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "accessRequestSettings": self.access_request_settings,
                "domain_restriction_settings": self.domain_restriction_settings,
                "permissionsInformation": self.permissions_information,
                "pickerSettings": self.picker_settings,
                "sharingAbilities": self.sharing_abilities,
                "sharingLinkTemplates": self.sharing_link_templates,
            }
            default_value = property_mapping.get(name, None)
        return super().get_property(name, default_value)

    @property
    def entity_type_name(self):
        return "SP.Sharing.SharingInformation"

    @property
    def address_bar_link_settings(self) -> AddressBarLinkSettings:
        """Gets the addressBarLinkSettings property"""
        from office365.sharepoint.sharing.address_bar_link_settings import (
            AddressBarLinkSettings,
        )

        return self.properties.get("addressBarLinkSettings", AddressBarLinkSettings())

    @property
    def age_group(self) -> Optional[int]:
        """Gets the ageGroup property"""
        return self.properties.get("ageGroup", None)

    @property
    def all_organization_security_group_id(self) -> Optional[UUID]:
        """Gets the allOrganizationSecurityGroupId property"""
        return self.properties.get("allOrganizationSecurityGroupId", None)

    @property
    def anyone_link_track_users(self) -> Optional[bool]:
        """Gets the anyoneLinkTrackUsers property"""
        return self.properties.get("anyoneLinkTrackUsers", None)

    @property
    def block_people_picker_and_sharing(self) -> Optional[bool]:
        """Gets the blockPeoplePickerAndSharing property"""
        return self.properties.get("blockPeoplePickerAndSharing", None)

    @property
    def can_add_existing_external_principal(self) -> Optional[bool]:
        """Gets the canAddExistingExternalPrincipal property"""
        return self.properties.get("canAddExistingExternalPrincipal", None)

    @property
    def can_add_external_principal(self) -> Optional[bool]:
        """Gets the canAddExternalPrincipal property"""
        return self.properties.get("canAddExternalPrincipal", None)

    @property
    def can_add_internal_principal(self) -> Optional[bool]:
        """Gets the canAddInternalPrincipal property"""
        return self.properties.get("canAddInternalPrincipal", None)

    @property
    def can_request_access_for_grant_access(self) -> Optional[bool]:
        """Gets the canRequestAccessForGrantAccess property"""
        return self.properties.get("canRequestAccessForGrantAccess", None)

    @property
    def can_send_email(self) -> Optional[bool]:
        """Gets the canSendEmail property"""
        return self.properties.get("canSendEmail", None)

    @property
    def can_use_simplified_roles(self) -> Optional[bool]:
        """Gets the canUseSimplifiedRoles property"""
        return self.properties.get("canUseSimplifiedRoles", None)

    @property
    def current_role(self) -> Optional[int]:
        """Gets the currentRole property"""
        return self.properties.get("currentRole", None)

    @property
    def customized_external_sharing_service_url(self) -> Optional[str]:
        """Gets the customizedExternalSharingServiceUrl property"""
        return self.properties.get("customizedExternalSharingServiceUrl", None)

    @property
    def default_link_kind(self) -> Optional[int]:
        """Gets the defaultLinkKind property"""
        return self.properties.get("defaultLinkKind", None)

    @property
    def default_share_link_permission(self) -> Optional[int]:
        """Gets the defaultShareLinkPermission property"""
        return self.properties.get("defaultShareLinkPermission", None)

    @property
    def default_share_link_scope(self) -> Optional[int]:
        """Gets the defaultShareLinkScope property"""
        return self.properties.get("defaultShareLinkScope", None)

    @property
    def default_share_link_to_existing_access(self) -> Optional[bool]:
        """Gets the defaultShareLinkToExistingAccess property"""
        return self.properties.get("defaultShareLinkToExistingAccess", None)

    @property
    def direct_url(self) -> Optional[str]:
        """Gets the directUrl property"""
        return self.properties.get("directUrl", None)

    @property
    def direct_url_legacy(self) -> Optional[str]:
        """Gets the directUrlLegacy property"""
        return self.properties.get("directUrlLegacy", None)

    @property
    def discoverable_by_organization_enabled(self) -> Optional[bool]:
        """Gets the discoverableByOrganizationEnabled property"""
        return self.properties.get("discoverableByOrganizationEnabled", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def enforce_ib_segment_filtering(self) -> Optional[bool]:
        """Gets the enforceIBSegmentFiltering property"""
        return self.properties.get("enforceIBSegmentFiltering", None)

    @property
    def enforce_spo_search(self) -> Optional[bool]:
        """Gets the enforceSPOSearch property"""
        return self.properties.get("enforceSPOSearch", None)

    @property
    def file_extension(self) -> Optional[str]:
        """Gets the fileExtension property"""
        return self.properties.get("fileExtension", None)

    @property
    def has_unique_permissions(self) -> Optional[bool]:
        """Gets the hasUniquePermissions property"""
        return self.properties.get("hasUniquePermissions", None)

    @property
    def is_consumer_files(self) -> Optional[bool]:
        """Gets the isConsumerFiles property"""
        return self.properties.get("isConsumerFiles", None)

    @property
    def is_multi_tenant_organization(self) -> Optional[bool]:
        """Gets the isMultiTenantOrganization property"""
        return self.properties.get("isMultiTenantOrganization", None)

    @property
    def is_premium(self) -> Optional[bool]:
        """Gets the isPremium property"""
        return self.properties.get("isPremium", None)

    @property
    def is_stub_file(self) -> Optional[bool]:
        """Gets the isStubFile property"""
        return self.properties.get("isStubFile", None)

    @property
    def item_unique_id(self) -> Optional[UUID]:
        """Gets the itemUniqueId property"""
        return self.properties.get("itemUniqueId", None)

    @property
    def item_url(self) -> Optional[str]:
        """Gets the itemUrl property"""
        return self.properties.get("itemUrl", None)

    @property
    def list_id(self) -> Optional[UUID]:
        """Gets the listId property"""
        return self.properties.get("listId", None)

    @property
    def microservice_share_ui_url(self) -> Optional[str]:
        """Gets the microserviceShareUiUrl property"""
        return self.properties.get("microserviceShareUiUrl", None)

    @property
    def outlook_endpoint_host_url(self) -> Optional[str]:
        """Gets the outlookEndpointHostUrl property"""
        return self.properties.get("outlookEndpointHostUrl", None)

    @property
    def recipient_limits(self) -> RecipientLimits:
        """Gets the recipientLimits property"""
        from office365.sharepoint.sharing.recipient_limits import RecipientLimits

        return self.properties.get("recipientLimits", RecipientLimits())

    @property
    def sensitivity_label_information(self) -> SensitivityLabelInformation:
        """Gets the sensitivityLabelInformation property"""
        from office365.sharepoint.sharing.sensitivitylabelinformation import (
            SensitivityLabelInformation,
        )

        return self.properties.get("sensitivityLabelInformation", SensitivityLabelInformation())

    @property
    def shared_object_type(self) -> Optional[int]:
        """Gets the sharedObjectType property"""
        return self.properties.get("sharedObjectType", None)

    @property
    def share_ui_url(self) -> Optional[str]:
        """Gets the shareUiUrl property"""
        return self.properties.get("shareUiUrl", None)

    @property
    def sharing_settings(self) -> ItemSharingSettings:
        """Gets the sharingSettings property"""
        from office365.sharepoint.sharing.itemsharingsettings import ItemSharingSettings

        return self.properties.get("sharingSettings", ItemSharingSettings())

    @property
    def sharing_status(self) -> Optional[int]:
        """Gets the sharingStatus property"""
        return self.properties.get("sharingStatus", None)

    @property
    def show_external_sharing_warning(self) -> Optional[bool]:
        """Gets the showExternalSharingWarning property"""
        return self.properties.get("showExternalSharingWarning", None)

    @property
    def site_ib_mode(self) -> Optional[str]:
        """Gets the siteIBMode property"""
        return self.properties.get("siteIBMode", None)

    @property
    def site_ib_segment_ids(self) -> StringCollection:
        """Gets the siteIBSegmentIDs property"""
        return self.properties.get("siteIBSegmentIDs", StringCollection())

    @property
    def site_id(self) -> Optional[UUID]:
        """Gets the siteId property"""
        return self.properties.get("siteId", None)

    @property
    def standard_roles_modified(self) -> Optional[bool]:
        """Gets the standardRolesModified property"""
        return self.properties.get("standardRolesModified", None)

    @property
    def substrate_file_id(self) -> Optional[str]:
        """Gets the substrateFileId property"""
        return self.properties.get("substrateFileId", None)

    @property
    def tenant_display_name(self) -> Optional[str]:
        """Gets the tenantDisplayName property"""
        return self.properties.get("tenantDisplayName", None)

    @property
    def tenant_id(self) -> Optional[str]:
        """Gets the tenantId property"""
        return self.properties.get("tenantId", None)

    @property
    def unique_access_groups(self) -> UniqueAccessGroupsWrapper:
        """Gets the uniqueAccessGroups property"""
        from office365.sharepoint.sharing.uniqueaccessgroupswrapper import (
            UniqueAccessGroupsWrapper,
        )

        return self.properties.get("uniqueAccessGroups", UniqueAccessGroupsWrapper())

    @property
    def user_is_sharing_via_mcs(self) -> Optional[str]:
        """Gets the userIsSharingViaMCS property"""
        return self.properties.get("userIsSharingViaMCS", None)

    @property
    def user_photo_cdn_base_url(self) -> Optional[str]:
        """Gets the userPhotoCdnBaseUrl property"""
        return self.properties.get("userPhotoCdnBaseUrl", None)

    @property
    def web_template_id(self) -> Optional[int]:
        """Gets the webTemplateId property"""
        return self.properties.get("webTemplateId", None)

    @property
    def web_url(self) -> Optional[str]:
        """Gets the webUrl property"""
        return self.properties.get("webUrl", None)
