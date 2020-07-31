from office365.graph.directory.directory_object_collection import DirectoryObjectCollection
from office365.graph.directory.group_setting_template import GroupSettingTemplate


class GroupSettingTemplateCollection(DirectoryObjectCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super(GroupSettingTemplateCollection, self).__init__(context, resource_path)
        self._item_type = GroupSettingTemplate
