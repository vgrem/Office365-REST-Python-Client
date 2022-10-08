from office365.sharepoint.base_entity import BaseEntity


class SignalStore(BaseEntity):
    """Provides methods for managing the analytics signal store."""

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Client.Search.Analytics.SignalStore"
