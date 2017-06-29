import requests

from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.context_web_information import ContextWebInformation
from office365.runtime.odata.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel
from office365.runtime.utilities.request_options import RequestOptions
from office365.sharepoint.site import Site
from office365.sharepoint.web import Web


class ClientContext(ClientRuntimeContext):
    """SharePoint client context"""

    def __init__(self, url, auth_context):
        super(ClientContext, self).__init__(url + "/_api/", auth_context)
        self.__web = None
        self.__site = None
        self.contextWebInformation = None
        self.json_format = JsonLightFormat(ODataMetadataLevel.Verbose)

    def ensure_form_digest(self, request_options):
        if not self.contextWebInformation:
            self.request_form_digest()
        request_options.set_header('X-RequestDigest', self.contextWebInformation.form_digest_value)

    def request_form_digest(self):
        """Request Form Digest"""
        request = RequestOptions(self.service_root_url + "contextinfo")
        self.authenticate_request(request)
        request.set_headers(self.json_format.build_http_headers())
        response = requests.post(url=request.url,
                                 headers=request.headers,
                                 auth=request.auth)
        payload = response.json()
        if self.json_format.metadata == ODataMetadataLevel.Verbose:
            payload = payload['d']['GetContextWebInformation']
        self.contextWebInformation = ContextWebInformation()
        self.contextWebInformation.from_json(payload)

    @property
    def web(self):
        """Get Web client object"""
        if not self.__web:
            self.__web = Web(self)
        return self.__web

    @property
    def site(self):
        """Get Site client object"""
        if not self.__site:
            self.__site = Site(self)
        return self.__site
