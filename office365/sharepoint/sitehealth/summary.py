from office365.sharepoint.base_entity import BaseEntity


class SiteHealthSummary(BaseEntity):
    """Specifies a summary of the results of running a set of site collection health rules."""

    @property
    def entity_type_name(self):
        return "SP.SiteHealth.SiteHealthSummary"
