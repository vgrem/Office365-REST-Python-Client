from __future__ import annotations

from requests import Response
from typing_extensions import Self

from office365.entity import Entity
from office365.runtime.http.request_options import RequestOptions


class PlannerEntity(Entity):
    """Base class for Planner resources.

    Microsoft Graph enforces optimistic concurrency for Planner: updates and
    deletes must carry an ``If-Match`` header holding the resource's latest
    ``@odata.etag``. This base class forwards that etag automatically whenever it
    is known, so the common ``entity.update().execute_query()`` /
    ``entity.delete_object().execute_query()`` flow just works.

    Because an update query has no return type, its response body is not
    deserialized, so the refreshed token is read from the response ``ETag``
    header (see :meth:`_capture_etag`) instead.
    """

    def _add_if_match_header(self, request: RequestOptions) -> None:
        etag = self.properties.get("__etag")
        if etag:
            request.set_header("If-Match", etag)

    def _prepare_update(self, request: RequestOptions) -> None:
        self._add_if_match_header(request)
        # Ask for the updated resource back so the response carries the new
        # ``ETag``; Planner ``PATCH`` returns ``204`` without it otherwise.
        request.set_header("Prefer", "return=representation")

    def _capture_etag(self, response: Response) -> None:
        """Store the response ``ETag`` header on this entity as ``__etag``.

        Keeps optimistic concurrency working across consecutive updates, whose
        response body (when requested via ``Prefer``) is not deserialized.
        """
        etag = response.headers.get("ETag")
        if etag:
            self.set_property("__etag", etag, False)

    def update(self) -> Self:
        super().update().before_execute(self._prepare_update)
        self.after_execute(self._capture_etag, include_response=True)
        return self

    def delete_object(self, *, ignore_missing: bool = False) -> Self:
        super().delete_object(ignore_missing=ignore_missing).before_execute(self._add_if_match_header)
        return self
