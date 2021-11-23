from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sharing.pickerSettings import PickerSettings


class SharePointSharingSettings(BaseEntity):

    @property
    def picker_properties(self):
        return self.properties.get('PickerProperties',
                                   PickerSettings(self.context, ResourcePath("PickerProperties", self.resource_path)))
