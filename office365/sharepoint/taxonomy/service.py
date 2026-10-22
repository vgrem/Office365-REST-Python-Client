from __future__ import annotations

from office365.runtime.odata.json_format import JsonProfile
from office365.runtime.odata.v4.json_format import V4JsonFormat
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.request import SharePointRequest
from office365.sharepoint.taxonomy.stores.store import TermStore


class TaxonomyService(ClientContext):
    """Wraps all of the associated TermStore objects for an Site object.

    Serves the term store from the ``_api/v2.1`` endpoint, which speaks OData V4,
    using its own request processor that reuses the source context's
    authentication and transport.
    """

    def __init__(self, context: ClientContext):
        super().__init__(context.base_url)
        self._pending_request = SharePointRequest(
            base_url=self._base_url,
            profile=self.profile,
        ).reuse(context.pending_request())

    @property
    def profile(self) -> JsonProfile:
        """The term store service speaks OData V4."""
        return V4JsonFormat()

    @property
    def service_root_url(self) -> str:
        """Get the API service root URL"""
        return f"{super().service_root_url}/v2.1"

    @property
    def term_store(self) -> TermStore:
        return TermStore(self, ResourcePath("termStore", None))
