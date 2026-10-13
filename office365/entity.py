from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from typing_extensions import Self

from office365.runtime.client_object import ClientObject
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.delete_entity import DeleteEntityQuery
from office365.runtime.queries.update_entity import UpdateEntityQuery
from office365.runtime.queries.upsert_entity import UpsertEntityQuery, raise_if_upsert_unsupported

if TYPE_CHECKING:
    from office365.graph_client import GraphClient


class Entity(ClientObject):
    """Base entity for Microsoft Graph objects with common CRUD operations."""

    def update(self) -> Self:
        """Updates the entity in Microsoft Graph.

        Returns:
            Self: The entity instance for method chaining

        Example:
            >>> client = GraphClient()
            >>> user = client.me
            >>> user.update().execute_query()
        """
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)
        return self

    def upsert(
        self,
        *,
        if_match: str | None = None,
        if_none_match: str | None = None,
    ) -> Self:
        """Creates or updates the entity with a single server-side ``PATCH``.

        The request is a ``PATCH`` carrying ``Prefer: create-if-missing,
        return=representation``: if the resource addressed by this entity exists
        it is updated, otherwise it is created, and the persisted representation
        is returned. The entity must be addressed by an alternate key or be a
        singleton so the service can identify it before creation.

        Not every endpoint supports server-side upsert. When it does not, the
        request raises
        :class:`~office365.runtime.exceptions.UpsertNotSupported` (chained to the
        server error) so the caller can fall back to a client-side
        lookup-then-write - for collections that is
        :meth:`~office365.entity_collection.EntityCollection.upsert`.

        Args:
            if_match: Optional ``If-Match`` value (optimistic concurrency).
            if_none_match: Optional ``If-None-Match`` value; ``"*"`` makes the
                request create-only (a no-op/``412`` when the resource exists).

        Returns:
            Self: The entity instance for method chaining.

        Example:
            >>> client = GraphClient()
            >>> group = client.groups.get_by_alternate_key("uniqueName", "contoso")
            >>> group.set_property("description", "Team site").upsert().execute_query()
        """
        qry = UpsertEntityQuery(self, if_match=if_match, if_none_match=if_none_match)
        self.context.add_query(qry)
        self.on_error(raise_if_upsert_unsupported)
        return self

    def update_properties(self, **properties: Any) -> Self:
        """Sets one or more properties and updates the entity in a single call.

        Sugar over repeated :meth:`set_property` calls followed by :meth:`update`:
        the values are coerced exactly as :meth:`set_property` does, and the
        request stays deferred until ``execute_query()`` runs.

        Args:
            **properties: Property names mapped to their new values. Use
                :meth:`set_property` instead for names that are not valid
                Python identifiers.

        Returns:
            Self: The entity instance for method chaining

        Example:
            >>> client = GraphClient()
            >>> client.me.update_properties(displayName="Jane", jobTitle="PM").execute_query()
        """
        for name, value in properties.items():
            self.set_property(name, value)
        return self.update()

    def delete_object(self, *, ignore_missing: bool = False) -> Self:
        """Deletes the entity from Microsoft Graph.

        Args:
            ignore_missing: When ``True``, deleting an entity that no longer
                exists (HTTP 404) succeeds instead of raising
                :class:`~office365.runtime.exceptions.ObjectNotFoundException`,
                which makes cleanup idempotent.

        Returns:
            Self: The entity instance for method chaining

        Example:
            >>> client = GraphClient()
            >>> client.users["mark@contoso.com"].delete_object(ignore_missing=True).execute_query()
        """
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self._tolerate_missing(ignore_missing)
        self.remove_from_parent_collection()
        return self

    @property
    def context(self) -> GraphClient:
        """Gets the GraphClient context for this entity.

        Returns:
            GraphClient: The parent client context
        """
        return cast("GraphClient", self._context)

    @property
    def entity_type_name(self) -> str:
        """Gets the Microsoft Graph type name for this entity.

        Returns:
            str: The fully qualified type name (e.g. "microsoft.graph.user")
        """
        if self._entity_type_name is None:
            name = type(self).__name__
            self._entity_type_name = "microsoft.graph." + name[0].lower() + name[1:]
        return self._entity_type_name

    @property
    def id(self) -> str | None:
        """Gets the unique identifier of the entity.

        Returns:
            Optional[str]: The entity ID if available, else None
        """
        return self.properties.get("id", None)

    @property
    def property_ref_name(self) -> str:
        """Gets the name of the key property used for entity reference.

        Returns:
            str: The property name used as entity key (default: "id")
        """
        return "id"

    def set_property(self, name: str, value: Any, persist_changes: bool = True) -> Self:
        """Sets a property value and updates the resource path if needed.

        Args:
            name: The property name to set
            value: The property value
            persist_changes: Whether to persist changes immediately

        Returns:
            Self: The entity instance for method chaining
        """
        super().set_property(name, value, persist_changes)
        if name == self.property_ref_name:
            if self._resource_path is None:
                if self.parent_collection is None:
                    self._resource_path = ResourcePath(value)
                elif isinstance(self.parent_collection.resource_path, EntityPath):
                    self._resource_path = EntityPath(value, self.parent_collection.resource_path.collection)
                else:
                    self._resource_path = ResourcePath(value, self.parent_collection.resource_path)
            else:
                self._resource_path.set_segment(value)
        return self
