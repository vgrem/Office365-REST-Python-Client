from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sharing.abilities import SharingAbilities
from office365.sharepoint.sharing.access_request_settings import AccessRequestSettings
from office365.sharepoint.sharing.links.default_templates_collection import SharingLinkDefaultTemplatesCollection
from office365.sharepoint.sharing.picker_settings import PickerSettings


class SharingInformation(BaseEntity):
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
    def picker_settings(self):
        """PickerSettings used by the PeoplePicker Control."""
        return self.properties.get('pickerSettings',
                                   PickerSettings(self.context, ResourcePath("pickerSettings", self.resource_path)))

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
                "pickerSettings": self.picker_settings,
                "sharingAbilities": self.sharing_abilities,
                "sharingLinkTemplates": self.sharing_link_templates
            }
            default_value = property_mapping.get(name, None)
        return super(SharingInformation, self).get_property(name, default_value)

    @property
    def entity_type_name(self):
        return "SP.Sharing.SharingInformation"
