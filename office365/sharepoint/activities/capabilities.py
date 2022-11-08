from office365.runtime.client_value import ClientValue


class ActivityCapabilities(ClientValue):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Activities.ActivityCapabilities"
