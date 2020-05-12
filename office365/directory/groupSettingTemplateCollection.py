from office365.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.directory.groupSettingTemplate import GroupSettingTemplate


class GroupSettingTemplateCollection(DirectoryObjectCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super(GroupSettingTemplateCollection, self).__init__(context, GroupSettingTemplate, resource_path)
