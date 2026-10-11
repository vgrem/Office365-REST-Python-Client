from office365.delta_collection import DeltaCollection
from office365.outlook.contacts.folders.folder import ContactFolder
from office365.runtime.deprecated import deprecated
from office365.runtime.odata.literals import escape_odata_string


class ContactFolderCollection(DeltaCollection[ContactFolder]):
    def __init__(self, context, resource_path=None):
        super().__init__(context, ContactFolder, resource_path)

    def add(self, display_name, **kwargs) -> ContactFolder:
        """Add a contact folder.

        Args:
            display_name (str): The contact folder's display name.
        """

        kwargs["displayName"] = display_name
        return super().add(**kwargs)

    def ensure(self, display_name: str) -> ContactFolder:
        """Gets an existing folder by name or creates it (idempotent)."""
        from office365.runtime.queries.get_or_create import create_or_get

        return create_or_get(
            create=lambda: self.add(display_name),
            find=lambda: self.find_by_name(display_name, required=True),
        )

    def find_by_name(self, display_name: str, *, required: bool = False) -> ContactFolder:
        """Look up a contact folder by its ``displayName``.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        folder matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            display_name (str): The contact folder display name
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"displayName eq '{escape_odata_string(display_name)}'", required=required)

    @deprecated("Use find_by_name() instead.", version="4.0")
    def get_by_name(self, display_name: str) -> ContactFolder:
        """Deprecated alias of :meth:`find_by_name` (strict)."""
        return self.find_by_name(display_name, required=True)
