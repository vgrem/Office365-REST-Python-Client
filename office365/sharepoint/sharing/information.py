from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sharing.picker_settings import PickerSettings


class SharingInformation(BaseEntity):
    """Represents a response for Microsoft.SharePoint.Client.Sharing.SecurableObjectExtensions.GetSharingInformation.
       The accessRequestSettings, domainRestrictionSettings and permissionsInformation properties are not included in
       the default scalar property set for this type.
    """

    @property
    def picker_settings(self):
        """PickerSettings used by the PeoplePicker Control."""
        return self.properties.get('pickerSettings',
                                   PickerSettings(self.context, ResourcePath("pickerSettings", self.resource_path)))
