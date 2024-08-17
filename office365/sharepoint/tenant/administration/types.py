from office365.runtime.client_value import ClientValue


class DisableGroupify(ClientValue):
    """ """


class AutoQuotaEnabled(ClientValue):
    """ """

    def __init__(self, is_read_only=None, value=None):
        self.IsReadOnly = is_read_only
        self.Value = value


class CreatePolicyRequest(ClientValue):
    """ """

    def __init__(self, is_preview_run=None, policy_custom_name=None):
        self.isPreviewRun = is_preview_run
        self.policyCustomName = policy_custom_name
