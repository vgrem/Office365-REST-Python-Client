from __future__ import annotations

from typing import Dict, Optional, cast

from office365.runtime.deprecated import deprecated
from office365.runtime.odata.literals import escape_odata_string
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.contenttypes.content_type import ContentType
from office365.sharepoint.contenttypes.creation_information import (
    ContentTypeCreationInformation,
)
from office365.sharepoint.contenttypes.entity_data import ContentTypeEntityData
from office365.sharepoint.entity_collection import EntityCollection


class ContentTypeCollection(EntityCollection[ContentType]):
    """Content Type resource collection"""

    def __init__(self, context, resource_path=None, parent=None):
        super().__init__(context, ContentType, resource_path, parent)

    def find_by_name(self, name: str, *, required: bool = False) -> ContentType:
        """Look up the content type with the given name from the collection.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        content type matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            name (str): Content type name
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"Name eq '{escape_odata_string(name)}'", required=required)

    @deprecated("Use find_by_name() instead.", version="4.0")
    def get_by_name(self, name: str) -> ContentType:
        """Deprecated alias of :meth:`find_by_name` (strict).

        Args:
            name (str): Content type name
        """
        return self.find_by_name(name, required=True)

    def get_by_id(self, content_type_id: str) -> ContentType:
        """Returns the content type with the given identifier from the collection.
        If a content type with the given identifier is not found in the collection, the server MUST return null.

        Args:
            content_type_id (str): A hexadecimal value representing the identifier of a content type.
        """
        return ContentType(
            self.context,
            ServiceOperationPath("GetById", [content_type_id], self.resource_path),
            self,
        )

    def ensure(
        self,
        name: str,
        description: str | None = None,
        group: str | None = None,
        *,
        content_type_id: str | None = None,
        on_conflict: str = "skip",
    ) -> ContentType:
        """Ensure a content type with the given name exists (idempotent).

        Looks the content type up by name and creates it only when missing, so a
        re-run is a no-op. With ``on_conflict="update"`` the existing content
        type's description and group are reconciled.

        Args:
            name: The content type name (the lookup key).
            description: The description to create it with.
            group: The group to create it with.
            content_type_id: The ``ContentTypeId`` to request. SharePoint Online
                assigns a content type its own identifier (and ignores this value
                at both list and web scope), so match content types by *name* —
                this is a best-effort hint for servers that do honour it.
            on_conflict: ``"skip"`` (default) or ``"update"``.
        """
        from office365.runtime.queries.get_or_create import get_or_create

        info = ContentTypeCreationInformation(Name=name, Description=description, Group=group, Id=content_type_id)

        def _reconcile(content_type: ContentType) -> None:
            changed = False
            if description is not None and content_type.description != description:
                content_type.set_property("Description", description)
                changed = True
            if group is not None and content_type.group != group:
                content_type.set_property("Group", group)
                changed = True
            if changed:
                content_type.update()

        return_type = self.find_by_name(name)
        return get_or_create(
            find=lambda: return_type,
            create_query=lambda: self._build_add_query(info, return_type),
            return_type=return_type,
            missing=lambda content_type: not content_type.is_loaded,
            on_conflict=on_conflict,
            reconcile=_reconcile,
        )

    def _build_add_query(
        self, content_type_info: ContentTypeCreationInformation, return_type: ContentType
    ) -> CreateEntityQuery:
        """Build (but do not queue) the ``Add`` query for the given content type spec."""
        params = cast(Dict, content_type_info.to_json())
        for k, v in params.items():
            if k == "Id":
                return_type.set_property(k, {"StringValue": v}, True)
            else:
                return_type.set_property(k, v, True)
        return CreateEntityQuery(self, return_type, return_type)

    def add(self, content_type_info: ContentTypeCreationInformation) -> ContentType:
        """Adds a new content type to the collection and returns a reference to the added SP.ContentType.

        Args:
            content_type_info (ContentTypeCreationInformation): Specifies properties that is to be used to construct the
                new content type.
        """
        return_type = ContentType(self.context)
        self.add_child(return_type)
        self.context.add_query(self._build_add_query(content_type_info, return_type))
        return return_type

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        group: Optional[str] = None,
        parent_content_type: Optional[ContentType] = None,
    ) -> ContentType:
        """Creates a new content type to the collection and returns a reference to the added SP.ContentType.

        Args:
            name (str): Specifies the name
            description (str): Specifies the description
            group (str): Specifies the group of the content type
            parent_content_type (str or ContentType): Specifies the parent content type (string identifier or object)
        """

        def _create(parent_content_type_id: Optional[str]):
            parameters = ContentTypeEntityData(name, description, group, parent_content_type_id)
            payload = {"parameters": parameters}
            qry = ServiceOperationQuery(self, "Create", None, payload, None, return_type)
            self.context.add_query(qry)

        return_type = ContentType(self.context)
        self.add_child(return_type)
        if isinstance(parent_content_type, ContentType):
            parent_content_type.ensure_property("StringId").after_execute(
                lambda _: _create(parent_content_type.string_id)
            )
        else:
            _create(parent_content_type)
        return return_type

    def add_available_content_type(self, content_type_id: str) -> ContentType:
        """Adds the specified content type to the content type collection.

        Args:
            content_type_id (str): Specifies the identifier of the content type to be added to the content type
                collection. It MUST exist in the web's available content types.
        """
        return_type = ContentType(self.context)
        self.add_child(return_type)
        qry = ServiceOperationQuery(self, "AddAvailableContentType", [content_type_id], None, None, return_type)
        self.context.add_query(qry)
        return return_type
