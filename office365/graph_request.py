from office365.runtime.odata.request import ODataRequest
from office365.runtime.odata.v4.json_format import V4JsonFormat

environments_endpoints = {
    "GCCH": {
        "graph_url": "https://graph.microsoft.com",
        "entra_url": "https://login.microsoftonline.com",
    },
    "GCC High": {
        "graph_url": "https://graph.microsoft.us",
        "entra_url": "https://login.microsoftonline.us",
    },
    "DoD": {
        "graph_url": "https://dod-graph.microsoft.us",
        "entra_url": "https://login.chinacloudapi.cn",
    },
}


class GraphRequest(ODataRequest):
    def __init__(self, version="v1.0", environment="GCCH"):
        # type: (str, str) -> None
        super(GraphRequest, self).__init__(V4JsonFormat())
        self._version = version
        self._environment_endpoints = environments_endpoints.get(environment, None)

    @property
    def service_root_url(self):
        # type: () -> str
        return "https://graph.microsoft.com/{0}".format(self._version)
