from office365.runtime.client_value import ClientValue


class SPOAppBillingProperties(ClientValue):
    """ """

    @property
    def entity_type_name(self):
        return (
            "Microsoft.Online.SharePoint.TenantAdministration.SPOAppBillingProperties"
        )
