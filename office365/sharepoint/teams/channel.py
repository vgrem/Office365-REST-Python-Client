from office365.sharepoint.base_entity import BaseEntity


class TeamChannel(BaseEntity):

    @property
    def folder_id(self):
        """
        :rtype: str or None
        """
        return self.properties.get("folderId", None)

    @property
    def group_id(self):
        """
        :rtype: str or None
        """
        return self.properties.get("groupId", None)
