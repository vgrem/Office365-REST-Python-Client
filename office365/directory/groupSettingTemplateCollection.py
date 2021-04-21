from office365.directory.groupSettingTemplate import GroupSettingTemplate
from office365.entity_collection import EntityCollection


class GroupSettingTemplateCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(GroupSettingTemplateCollection, self).__init__(context, GroupSettingTemplate, resource_path)
