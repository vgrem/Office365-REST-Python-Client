from office365.graph.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.graph.directory.groupSettingTemplate import GroupSettingTemplate


class GroupSettingTemplateCollection(DirectoryObjectCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super(GroupSettingTemplateCollection, self).__init__(context, resource_path)
        self._item_type = GroupSettingTemplate
