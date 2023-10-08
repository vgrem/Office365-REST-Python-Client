from office365.sharepoint.entity import Entity


class ModernizeHomepageResult(Entity):
    """"""

    @property
    def can_modernize_homepage(self):
        """
        :rtype: bool or None
        """
        return self.properties.get("CanModernizeHomepage", None)
