from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sharing.pickerSettings import PickerSettings


class SharingInformation(BaseEntity):

    @property
    def picker_settings(self):
        return self.properties.get('pickerSettings',
                                   PickerSettings(self.context, ResourcePath("pickerSettings", self.resource_path)))
