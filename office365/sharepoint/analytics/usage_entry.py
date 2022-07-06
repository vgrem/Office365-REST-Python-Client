from office365.sharepoint.base_entity import BaseEntity


class AnalyticsUsageEntry(BaseEntity):
    """Specifies an analytics usage entry to log user or system events"""

    @property
    def entity_type_name(self):
        return "SP.Analytics.AnalyticsUsageEntry"
