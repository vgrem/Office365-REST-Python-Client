from office365.sharepoint.base_entity import BaseEntity


class InformationRightsManagementSettings(BaseEntity):
    """Represents the Information Rights Management (IRM) settings of a list in Microsoft SharePoint Foundation."""

    @property
    def policy_title(self):
        """
        Specifies the permission policy title.

        :rtype: str or None
        """
        return self.properties.get("PolicyTitle", None)

    @property
    def policy_description(self):
        """
        Specifies the permission policy description.

        :rtype: str or None
        """
        return self.properties.get("PolicyDescription", None)

    @property
    def group_name(self):
        """
        Specifies the group name (email address) that the permission is also applicable to.

        :rtype: str or None
        """
        return self.properties.get("GroupName", None)


