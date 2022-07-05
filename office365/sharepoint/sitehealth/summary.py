from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sitehealth.result import SiteHealthResult


class SiteHealthSummary(BaseEntity):
    """Specifies a summary of the results of running a set of site collection health rules."""

    @property
    def results(self):
        """Specifies a list of site collection health rule results, one for each site collection health rule that
        was run."""
        return self.properties.get("Results", ClientValueCollection(SiteHealthResult))

    @property
    def entity_type_name(self):
        return "SP.SiteHealth.SiteHealthSummary"
