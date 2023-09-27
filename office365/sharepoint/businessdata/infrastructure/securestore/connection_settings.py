from office365.sharepoint.base_entity import BaseEntity


class ConnectionSettings(BaseEntity):
    """"""

    @property
    def entity_type_name(self):
        return "Microsoft.BusinessData.Infrastructure.SecureStore.ConnectionSettings"
