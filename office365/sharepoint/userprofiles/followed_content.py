from office365.sharepoint.base_entity import BaseEntity


class FollowedContent(BaseEntity):
    """The FollowedContent class provides access to followed content items."""

    @property
    def followed_documents_url(self):
        """
        The FollowedDocumentsUrl property gets the location of the followed documents view.

        :rtype: str or None
        """
        return self.properties.get("FollowedDocumentsUrl", None)

    @property
    def followed_sites_url(self):
        """
        The FollowedSitesUrl property gets the location of the followed sites view.

        :rtype: str or None
        """
        return self.properties.get("FollowedSitesUrl", None)

    @property
    def entity_type_name(self):
        return "SP.UserProfiles.FollowedContent"
