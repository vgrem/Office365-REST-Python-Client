from office365.runtime.client_value import ClientValue


class ActivityIdentityItem(ClientValue):

    def __init__(self, client_id=None):
        """
        :param str client_id:
        """
        self.clientId = client_id

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Activities.ActivityIdentityItem"

