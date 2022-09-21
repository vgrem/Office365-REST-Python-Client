from office365.sharepoint.base_entity import BaseEntity


class PromotedSites(BaseEntity):
    """
    The PromotedSites object provides access to a collection of site links that are visible to all users.
    """

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Portal.UserProfiles.PromotedSites"
