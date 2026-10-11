from __future__ import annotations

from typing_extensions import Self

from office365.directory.permissions.require_permission import require_permission
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.workbooks.applications.application import WorkbookApplication
from office365.onedrive.workbooks.comments.comment import WorkbookComment
from office365.onedrive.workbooks.functions.functions import WorkbookFunctions
from office365.onedrive.workbooks.names.collection import WorkbookNamedItemCollection
from office365.onedrive.workbooks.operations.workbook import WorkbookOperation
from office365.onedrive.workbooks.session_info import WorkbookSessionInfo
from office365.onedrive.workbooks.tables.collection import WorkbookTableCollection
from office365.onedrive.workbooks.worksheets.collection import (
    WorkbookWorksheetCollection,
)
from office365.runtime.client_result import ClientResult
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.limits import Limit, LimitKind, limit
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery

_DOC = "https://learn.microsoft.com/en-us/graph/throttling-limits"


@limit(
    Limit("excel", 5_000, LimitKind.SUPPORTED, "requests", "app", doc=_DOC, window_seconds=10),
    Limit("excel", 1_500, LimitKind.SUPPORTED, "requests", "app+tenant", doc=_DOC, window_seconds=10),
)
class Workbook(Entity):
    """The top-level object that contains related workbook objects such as worksheets, tables, and ranges."""

    @require_permission(delegated=["Files.ReadWrite"], application=["Files.ReadWrite"])
    def session_info_resource(self) -> ClientResult[WorkbookSessionInfo]:
        return_type = ClientResult(self.context, WorkbookSessionInfo())
        qry = FunctionQuery(self, "sessionInfoResource", None, return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(delegated=["Files.ReadWrite"], application=["Files.ReadWrite"])
    def create_session(self, persist_changes: bool | None = None) -> ClientResult[WorkbookSessionInfo]:
        """Create a new workbook session.

        Excel APIs can be called in one of two modes:
        Persistent session - All changes made to the workbook are persisted (saved). This is the usual mode of
        operation.
        Non-persistent session - Changes made by the API are not saved to the source location. Instead, the Excel
        backend server keeps a temporary copy of the file that reflects the changes made during that particular
        API session. When the Excel session expires, the changes are lost. This mode is useful for apps that
        need to do analysis or obtain the results of a calculation or a chart image, but not affect the
        document state.

        Args:
            persist_changes (bool): Determines whether persist changes
        """
        payload = {"persistChanges": persist_changes}
        return_type = ClientResult(self.context, WorkbookSessionInfo())
        qry = ServiceOperationQuery(self, "createSession", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(delegated=["Files.ReadWrite"], application=["Files.ReadWrite"])
    def refresh_session(self, session_id: str) -> Self:
        """Use this API to refresh an existing workbook session.

        Args:
            session_id (str): Identifier of the workbook session
        """

        def _construct_request(request: RequestOptions) -> None:
            request.set_header("workbook-session-id", session_id)

        qry = ServiceOperationQuery(self, "refreshSession")
        self.context.add_query(qry).before_execute(_construct_request)
        return self

    @require_permission(delegated=["Files.ReadWrite"], application=["Files.ReadWrite"])
    def close_session(self, session_id: str) -> Self:
        """Use this API to close an existing workbook session.

        Args:
            session_id (str): Identifier of the workbook session
        """
        qry = ServiceOperationQuery(self, "closeSession")

        def _construct_request(request: RequestOptions) -> None:
            request.set_header("workbook-session-id", session_id)

        self.context.add_query(qry).before_execute(_construct_request)
        return self

    @property
    def application(self) -> WorkbookApplication:
        """"""
        return self.properties.get(
            "application",
            WorkbookApplication(self.context, ResourcePath("application", self.resource_path)),
        )

    @property
    def comments(self) -> EntityCollection[WorkbookComment]:
        """"""
        return self.properties.get(
            "comments",
            EntityCollection(
                self.context,
                WorkbookComment,
                ResourcePath("comments", self.resource_path),
            ),
        )

    @property
    def functions(self) -> WorkbookFunctions:
        """"""
        return self.properties.get(
            "functions",
            WorkbookFunctions(self.context, ResourcePath("functions", self.resource_path)),
        )

    @property
    def tables(self) -> WorkbookTableCollection:
        """Represents a collection of tables associated with the workbook. Read-only."""
        return self.properties.get(
            "tables",
            WorkbookTableCollection(self.context, ResourcePath("tables", self.resource_path)),
        )

    @property
    def names(self) -> WorkbookNamedItemCollection:
        """Represents a collection of workbook scoped named items (named ranges and constants). Read-only."""
        return self.properties.get(
            "names",
            WorkbookNamedItemCollection(
                self.context,
                ResourcePath("names", self.resource_path),
            ),
        )

    @property
    def operations(self) -> EntityCollection[WorkbookOperation]:
        """The status of workbook operations. Getting an operation collection is not supported, but you can get the
        status of a long-running operation if the Location header is returned in the response
        """
        return self.properties.get(
            "operations",
            EntityCollection(
                self.context,
                WorkbookOperation,
                ResourcePath("operations", self.resource_path),
            ),
        )

    @property
    def worksheets(self) -> WorkbookWorksheetCollection:
        """Represents a collection of worksheets associated with the workbook. Read-only."""
        return self.properties.get(
            "worksheets",
            WorkbookWorksheetCollection(self.context, ResourcePath("worksheets", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Workbook"
