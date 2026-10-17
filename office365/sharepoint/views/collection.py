from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, cast

from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.views.create_information import ViewCreationInformation
from office365.sharepoint.views.type import ViewType
from office365.sharepoint.views.view import View

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.lists.list import List

#: Maps the REST ``ViewType`` string (returned by a read) to the integer
#: ``ViewTypeKind`` the ``Add`` service operation expects — and back.
_VIEW_TYPE_KIND_BY_NAME = {
    "NONE": ViewType.NoneType,
    "HTML": ViewType.Html,
    "GRID": ViewType.Grid,
    "CALENDAR": ViewType.Calendar,
    "RECURRENCE": ViewType.Recurrence,
    "CHART": ViewType.Chart,
    "GANTT": ViewType.Gantt,
}
_VIEW_TYPE_NAME_BY_KIND = {kind: name for name, kind in _VIEW_TYPE_KIND_BY_NAME.items()}


def _view_type_kind(view_type: int | str | None) -> int | None:
    """Normalize a view type (name or integer kind) to the integer kind."""
    if isinstance(view_type, str):
        return _VIEW_TYPE_KIND_BY_NAME.get(view_type.upper())
    return view_type


def _view_type_name(view_type: int | str | None) -> str | None:
    """Normalize a view type (name or integer kind) to the canonical name."""
    if isinstance(view_type, str):
        return view_type.upper()
    if isinstance(view_type, int):
        return _VIEW_TYPE_NAME_BY_KIND.get(view_type)
    return None


class ViewCollection(EntityCollection[View]):
    """Represents a collection of View resources."""

    def __init__(
        self,
        context: ClientContext,
        resource_path: Optional[ResourcePath] = None,
        parent_list: Optional[List] = None,
    ) -> None:
        super().__init__(context, View, resource_path, parent_list)

    def add(self, information: ViewCreationInformation) -> View:
        """Add a new list view to the collection.

        Args:
            information: The view properties to create.
        """
        return_type = View(self.context, None, self.parent_list)  # type: ignore[arg-type]
        self.context.add_query(self._build_add_query(information, return_type))
        return return_type

    def _build_add_query(self, information: ViewCreationInformation, return_type: View) -> ServiceOperationQuery:
        """Build (but do not queue) an ``Add`` query for the given view."""
        self.add_child(return_type)
        payload = {"parameters": information}
        return ServiceOperationQuery(self, "Add", None, payload, None, return_type)

    @staticmethod
    def _creation_info(
        title: str,
        fields: list[str] | None,
        row_limit: int | None,
        view_type: int | str | None,
        paged: bool | None,
        personal_view: bool | None,
        **kwargs: Any,
    ) -> ViewCreationInformation:
        """Build a :class:`ViewCreationInformation` from the create/ensure parameters."""
        return ViewCreationInformation(
            Title=title,
            ViewFields=StringCollection(fields),
            RowLimit=row_limit,
            ViewTypeKind=_view_type_kind(view_type),
            Paged=paged,
            PersonalView=personal_view,
            **kwargs,
        )

    def get_by_title(self, view_title: str) -> View:
        """Get a view by title.

        If multiple views share the same title the server determines
        which one to return.

        Args:
            view_title: The title of the view to return.
        """
        return View(
            self.context,
            ServiceOperationPath("GetByTitle", [view_title], self.resource_path),
            self._parent,  # type: ignore[arg-type]
        )

    def get_by_id(self, view_id: str) -> View:
        """Get a view by its ID.

        Args:
            view_id: The identifier of the view to return.
        """
        return View(
            self.context,
            ServiceOperationPath("GetById", [view_id], self.resource_path),
            self._parent,  # type: ignore[arg-type]
        )

    def create(
        self,
        title: str,
        fields: list[str] | None = None,
        row_limit: int | None = None,
        view_type: int | str | None = None,
        paged: bool | None = None,
        personal_view: bool | None = None,
        **kwargs: Any,
    ) -> View:
        """Create a new list view with primitive parameters.

        Creates a new list view

        Args:
            title: The display name of the view.
            fields: Internal names of fields to include in the view.
            row_limit: Maximum number of items per page.
            view_type: View kind — either an integer ``ViewTypeKind`` or its name
                (``"HTML"``, ``"GRID"``, ``"CALENDAR"``, ...). A read returns
                the name; the ``Add`` operation expects the integer.
            paged: Whether the view supports paging.
            personal_view: If True, creates a personal (user-specific) view.
            **kwargs: Additional ``ViewCreationInformation`` properties.

        Returns:
            The new ``View`` (not yet executed).
        """
        info = self._creation_info(title, fields, row_limit, view_type, paged, personal_view, **kwargs)
        return self.add(info)

    def ensure_view(
        self,
        title: str,
        fields: list[str] | None = None,
        row_limit: int | None = None,
        view_type: int | str | None = None,
        paged: bool | None = None,
        personal_view: bool | None = None,
        *,
        on_conflict: str = "skip",
        **kwargs: Any,
    ) -> View:
        """Ensure a list view exists, creating it when missing (idempotent).

        The view is matched by title (via :meth:`get_by_title`). Fully deferred:
        run the returned chain with ``execute_query()``. When the view already
        exists it is reused; with ``on_conflict="update"`` the scalar view
        settings (``row_limit``, ``view_type``, ``paged``, ``personal_view``) are
        reconciled. View fields are applied only when the view is created, so a
        re-run never rewrites an existing view's columns.

        Args:
            title: The display name of the view (the match key).
            fields: Internal names of fields to include when creating the view.
            row_limit: Maximum number of items per page.
            view_type: View kind — either an integer ``ViewTypeKind`` or its name
                (``"HTML"``, ``"GRID"``, ``"CALENDAR"``, ...). A read returns
                the name; the ``Add`` operation expects the integer.
            paged: Whether the view supports paging.
            personal_view: If True, creates a personal (user-specific) view.
            on_conflict: ``"skip"`` (keep the existing view) or ``"update"``
                (reconcile its scalar settings).
            **kwargs: Additional ``ViewCreationInformation`` properties (create only).

        Returns:
            The existing or newly created ``View``.

        Example:
            >>> view = lst.views.ensure_view("Active", fields=["Title", "Modified"]).execute_query()
        """
        from office365.runtime.queries.get_or_create import get_or_create

        info = self._creation_info(title, fields, row_limit, view_type, paged, personal_view, **kwargs)
        return_type = self.get_by_title(title)

        def _reconcile(view: View) -> None:
            changed = False
            if row_limit is not None and view.row_limit != row_limit:
                view.row_limit = row_limit
                changed = True
            if view_type is not None and (view.view_type or "").upper() != _view_type_name(view_type):
                view.set_property("ViewType", _view_type_name(view_type))
                changed = True
            if paged is not None and view.paged != paged:
                view.set_property("Paged", paged)
                changed = True
            if personal_view is not None and view.personal_view != personal_view:
                view.set_property("PersonalView", personal_view)
                changed = True
            if changed:
                view.update()

        return get_or_create(
            find=return_type.get,
            create_query=lambda: self._build_add_query(info, return_type),
            return_type=return_type,
            # GetByTitle answers HTTP 200 with an empty body for a missing view
            # (not 404), so a tolerant predicate is required to create it.
            missing=lambda view: not view.is_loaded,
            on_conflict=on_conflict,
            reconcile=_reconcile,
        )

    @property
    def parent_list(self) -> List:
        """Return the parent list of this view collection."""
        from office365.sharepoint.lists.list import List

        return cast(List, self._parent)
