from office365.sharepoint.base_entity import BaseEntity


class ModernizeHomepageResult(BaseEntity):
    """"""

    @property
    def can_modernize_homepage(self):
        """
        :rtype: bool or None
        """
        return self.properties.get("CanModernizeHomepage", None)
