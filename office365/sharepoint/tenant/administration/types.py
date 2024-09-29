from office365.runtime.client_value import ClientValue


class DisableGroupify(ClientValue):
    """ """


class AutoQuotaEnabled(ClientValue):
    """Automatic quota management type"""

    def __init__(self, is_read_only=None, value=None):
        self.IsReadOnly = is_read_only
        self.Value = value

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.AutoQuotaEnabled"


class CreatePolicyRequest(ClientValue):
    """ """

    def __init__(self, is_preview_run=None, policy_custom_name=None):
        """
        :param bool is_preview_run:
        :param str policy_custom_name:
        """
        self.isPreviewRun = is_preview_run
        self.policyCustomName = policy_custom_name

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.CreatePolicyRequest"
