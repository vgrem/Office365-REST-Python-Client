from office365.entity_collection import EntityCollection
from office365.onenote.sections.section import OnenoteSection
from office365.runtime.odata.literals import escape_odata_string


class OnenoteSectionCollection(EntityCollection[OnenoteSection]):
    """OneNote section's collection"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, OnenoteSection, resource_path)

    def find_by_display_name(self, display_name: str, *, required: bool = False) -> OnenoteSection:
        """Look up a section by its ``displayName``.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        section matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            display_name (str): The section display name
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"displayName eq '{escape_odata_string(display_name)}'", required=required)

    def ensure(self, display_name: str) -> OnenoteSection:
        """Return the section with the given name, creating it when absent (idempotent).

        Deferred — resolve with ``execute_query()``. OneNote rejects a duplicate
        section name (``20117``, classified as
        :class:`~office365.runtime.exceptions.DuplicatedObjectException`), so the
        create-first helper is safe and a re-run is a no-op:

            section = notebook.sections.ensure("Meeting Notes").execute_query()

        Args:
            display_name (str): The section display name

        Returns:
            OnenoteSection: The existing or newly created section
        """
        from office365.runtime.queries.get_or_create import create_or_get

        return create_or_get(
            create=lambda: self.add(displayName=display_name),
            find=lambda: self.find_by_display_name(display_name, required=True),
        )
