from office365.sharepoint.base_entity import BaseEntity


class ReorderingRuleCollection(BaseEntity):
    """Contains information about how to reorder the search results."""

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Client.Search.Query.ReorderingRuleCollection"
