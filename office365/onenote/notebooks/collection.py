from office365.directory.permissions.require_permission import require_permission
from office365.entity_collection import EntityCollection
from office365.onenote.notebooks.copy_notebook_model import CopyNotebookModel
from office365.onenote.notebooks.notebook import Notebook
from office365.onenote.notebooks.recent import RecentNotebook
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.odata.literals import escape_odata_string
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery


class NotebookCollection(EntityCollection[Notebook]):
    def __init__(self, context, resource_path=None):
        super().__init__(context, Notebook, resource_path)

    def find_by_display_name(self, display_name: str, *, required: bool = False) -> Notebook:
        """Look up a notebook by its ``displayName``.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        notebook matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            display_name (str): The notebook display name
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"displayName eq '{escape_odata_string(display_name)}'", required=required)

    @require_permission(
        delegated=["Notes.Create", "Notes.ReadWrite", "Notes.ReadWrite.All"], application=["Notes.ReadWrite.All"]
    )
    def add(self, display_name: str) -> Notebook:
        """Create a new OneNote notebook.

        Args:
            display_name (str): Name for the notebook. Notebook names must be unique. The name cannot contain more
              than 128 characters or contain the following characters: ?*/:<>|'"
        """
        return super().add(displayName=display_name)

    def ensure(self, display_name: str) -> Notebook:
        """Return the notebook with the given name, creating it when absent (idempotent).

        Deferred — resolve with ``execute_query()``. OneNote rejects a duplicate
        notebook name (``20117``, classified as
        :class:`~office365.runtime.exceptions.DuplicatedObjectException`), so the
        create-first helper is safe and a re-run is a no-op:

            notebook = client.me.onenote.notebooks.ensure("Project X").execute_query()

        Args:
            display_name (str): The notebook display name

        Returns:
            Notebook: The existing or newly created notebook
        """
        from office365.runtime.queries.get_or_create import create_or_get

        return create_or_get(
            create=lambda: self.add(display_name),
            find=lambda: self.find_by_display_name(display_name, required=True),
        )

    @require_permission(
        delegated=["Notes.Read", "Notes.Read.All", "Notes.ReadWrite", "Notes.ReadWrite.All"],
        application=["Notes.Read.All", "Notes.ReadWrite.All"],
    )
    def get_notebook_from_web_url(self, web_url: str) -> ClientResult[CopyNotebookModel]:
        """Retrieve the properties and relationships of a notebook object by using its URL path.
        The location can be user notebooks on Microsoft 365, group notebooks,
        or SharePoint site-hosted team notebooks on Microsoft 365.

        Args:
            web_url (str): The URL path of the notebook to retrieve. It can also contain a "onenote:" prefix.
        """
        return_type = ClientResult(self.context, CopyNotebookModel())
        params = {"webUrl": web_url}
        qry = ServiceOperationQuery(self, "getNotebookFromWebUrl", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(
        delegated=["Notes.Read", "Notes.Read.All", "Notes.ReadWrite", "Notes.ReadWrite.All"],
        application=["Notes.Read.All", "Notes.ReadWrite.All"],
    )
    def get_recent_notebooks(
        self, include_personal_notebooks: bool = True
    ) -> ClientResult[ClientValueCollection[RecentNotebook]]:
        """Get a list of recentNotebook instances that have been accessed by the signed-in user.

        Args:
            include_personal_notebooks (bool): Include notebooks owned by the user. Set to true to include notebooks
              owned by the user; otherwise, set to false. If you don't include the includePersonalNotebooks parameter,
              your request will return a 400 error response.
        """

        return_type = ClientResult(self.context, ClientValueCollection(RecentNotebook))
        params = {"includePersonalNotebooks": include_personal_notebooks}
        qry = FunctionQuery(self, "getRecentNotebooks", params, return_type)
        self.context.add_query(qry)
        return return_type
