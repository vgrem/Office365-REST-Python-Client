from office365.runtime.client_value import ClientValue


class GroupCreationContext(ClientValue):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Portal.GroupCreationContext"
