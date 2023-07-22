from office365.runtime.client_value import ClientValue


class ActivityClientRequest(ClientValue):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Activities.ActivityClientRequest"
