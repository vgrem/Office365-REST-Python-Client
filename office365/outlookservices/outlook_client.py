from office365.outlookservices.user import User
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.odata.v4_json_format import V4JsonFormat
from office365.runtime.resource_path_entry import ResourcePathEntry


class OutlookClient(ClientRuntimeContext):
    """Office365 Outlook client context"""

    def __init__(self, ctx_auth):
        self.__service_root_url = "https://outlook.office365.com/api/v1.0/"
        super(OutlookClient, self).__init__(self.__service_root_url, ctx_auth)
        self.json_format = V4JsonFormat("minimal")

    @property
    def me(self):
        """The Me endpoint is provided as a shortcut for specifying the current user by SMTP address."""
        return User(self, ResourcePathEntry(self, None, "me"))


