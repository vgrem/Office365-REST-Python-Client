from office365.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.directory.groupSettingTemplate import GroupSettingTemplate


class GroupSettingTemplateCollection(DirectoryObjectCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, resource_path)
        self._item_type = GroupSettingTemplate
