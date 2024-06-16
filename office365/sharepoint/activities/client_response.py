from office365.runtime.client_value import ClientValue


class ActivityClientResponse(ClientValue):
    """"""

    def __init__(self, id_, message=None, serverId=None, status=None):
        # type: (str, str, str, int) -> None
        """ """
        self.id = id_
        self.message = message
        self.serverId = serverId
        self.status = status

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Activities.ActivityClientResponse"
