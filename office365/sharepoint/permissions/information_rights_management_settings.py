from office365.sharepoint.base_entity import BaseEntity


class InformationRightsManagementSettings(BaseEntity):

    @property
    def policy_title(self):
        """
        :rtype: str or None
        """
        return self.properties.get("PolicyTitle", None)

    @property
    def policy_description(self):
        """
        :rtype: str or None
        """
        return self.properties.get("PolicyDescription", None)

    @property
    def group_name(self):
        """
        :rtype: str or None
        """
        return self.properties.get("GroupName", None)
