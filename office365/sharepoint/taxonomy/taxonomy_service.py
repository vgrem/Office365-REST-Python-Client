from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.odata.odata_request import ODataRequest
from office365.runtime.odata.v4_json_format import V4JsonFormat
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.taxonomy.term_store import TermStore


class TaxonomyService(ClientRuntimeContext):
    """Wraps all of the associated TermStore objects for an Site object."""

    def __init__(self, context):
        """

        :param ClientContext context:
        """
        super().__init__(context)
        self._pendingRequest = ODataRequest(self, V4JsonFormat("minimal"))
        self._service_root_url = f"{context.service_root_url()}v2.1/"

    def pending_request(self):
        return self._pendingRequest

    def service_root_url(self):
        return self._service_root_url

    @property
    def term_store(self):
        return TermStore(self, ResourcePath("termStore", None))
