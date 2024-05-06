from office365.runtime.client_value import ClientValue


class RecentAdminActionReport(ClientValue):
    """ """

    def __init__(self, actions=None, createdByEmail=None):
        # type: (str, str) -> None
        self.actions = actions
        self.createdByEmail = createdByEmail

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Administration.TenantAdmin.RecentAdminActionReport"
