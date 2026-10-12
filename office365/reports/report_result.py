from __future__ import annotations

import csv
import io
from typing import TYPE_CHECKING, cast

from typing_extensions import Self

from office365.reports.report import Report
from office365.runtime.client_result import ClientResult

if TYPE_CHECKING:
    from office365.runtime.client_runtime_context import ClientRuntimeContext


class ReportResult(ClientResult[Report]):
    """The result of a report call.

    A typed :class:`~office365.runtime.client_result.ClientResult` whose value is
    a :class:`~office365.reports.report.Report`. It adds the CSV conveniences the
    usage reports need, so callers don't reach through ``.value``::

        rows = client.reports.get_email_activity_counts("D30").execute_query().csv_rows()

    ``execute_query()`` / ``execute_query_async()`` return ``Self`` so the call
    chains without losing the type.
    """

    def __init__(self, context: ClientRuntimeContext) -> None:
        # Seed an empty ``Report``: the runtime's raw-payload branch
        # (``set_property("__value", ...)``) then fills ``Report.content``
        # instead of replacing ``.value`` with the raw bytes.
        super().__init__(context, Report())

    def to_text(self) -> str:
        """Returns the report content as text.

        Graph prefixes the CSV with a UTF-8 BOM, so it is decoded with
        ``utf-8-sig`` — a plain ``utf-8`` decode would leave the first column
        named ``"\\ufeffReport Date"`` and every lookup would silently return
        ``None``.
        """
        return self.to_bytes().decode("utf-8-sig")

    def csv_rows(self) -> list[dict[str, str]]:
        """Parses the CSV report content into row dicts keyed by column name."""
        return list(csv.DictReader(io.StringIO(self.to_text())))

    def execute_query(self) -> Self:
        """Submit the deferred query and return this result for chaining."""
        return cast(Self, super().execute_query())

    async def execute_query_async(self) -> Self:
        """Submit the deferred query and return this result for chaining."""
        return cast(Self, await super().execute_query_async())
