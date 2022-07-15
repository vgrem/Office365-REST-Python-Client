from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.odata.request import ODataRequest
from office365.runtime.odata.v4.json_format import V4JsonFormat
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.taxonomy.store import TermStore


class TaxonomyService(ClientRuntimeContext):
    """Wraps all of the associated TermStore objects for an Site object."""

    def __init__(self, context):
        """
        :type  context: office365.sharepoint.client_context.ClientContext
        """
        super(TaxonomyService, self).__init__()
        self._auth_context = context.authentication_context
        self._pendingRequest = ODataRequest(self, V4JsonFormat())
        self._service_root_url = "{0}/v2.1".format(context.service_root_url())

    def authenticate_request(self, request):
        self._auth_context.authenticate_request(request)

    def pending_request(self):
        return self._pendingRequest

    def service_root_url(self):
        return self._service_root_url

    @property
    def term_store(self):
        return TermStore(self, ResourcePath("termStore", None))
