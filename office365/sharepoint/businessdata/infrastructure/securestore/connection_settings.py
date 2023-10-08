from office365.sharepoint.entity import Entity


class ConnectionSettings(Entity):
    """"""

    @property
    def entity_type_name(self):
        return "Microsoft.BusinessData.Infrastructure.SecureStore.ConnectionSettings"
