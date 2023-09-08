from office365.runtime.client_value import ClientValue


class ActivityClientResponse(ClientValue):
    """"""

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Activities.ActivityClientResponse"
