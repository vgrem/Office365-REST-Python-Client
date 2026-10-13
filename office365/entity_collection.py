from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union, cast

from office365.entity import Entity
from office365.runtime.client_object import ClientObjectT
from office365.runtime.paths.alternate_key import AlternateKeyPath
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.record_collection import RecordCollection

if TYPE_CHECKING:
    from office365.graph_client import GraphClient


class EntityCollection(RecordCollection[ClientObjectT]):
    """A collection container which represents a named collections of entities"""

    def __init__(
        self,
        context: GraphClient,
        item_type: Type[ClientObjectT],
        resource_path: Optional[ResourcePath] = None,
        parent: Optional[Entity] = None,
    ) -> None:
        super().__init__(context, item_type, resource_path, parent)

    def __getitem__(self, key: Union[int, str]) -> ClientObjectT:
        """Args:
        key (int or str): key is used to address an entity by either an index or by identifier
        """
        if isinstance(key, int):
            return super().__getitem__(key)
        elif isinstance(key, str):
            return self.create_typed_object(resource_path=EntityPath(key, self._canonical_collection()))
        else:
            raise ValueError("Invalid key: expected either an entity index [int] or identifier [str]")

    def get_by_alternate_key(self, key_name: str, key_value: Union[int, str]) -> ClientObjectT:
        """Addresses a single entity by one of its alternate keys.

        Builds the parenthesised OData path ``.../<collection>(<key>='<value>')``
        instead of a ``$filter`` lookup, so the entity is fetched by URL directly.
        Deferred — resolve with ``execute_query()``. Use it for the keys Microsoft
        Graph declares as alternate keys, for example::

            group = client.groups.get_by_alternate_key("uniqueName", "Group157")

        Args:
            key_name (str): The alternate-key property name (e.g. ``uniqueName``).
            key_value (object): The alternate-key value.
        """
        return self.create_typed_object(
            resource_path=AlternateKeyPath(key_name, key_value, self._canonical_collection())
        )

    def add(self, *args: Any, **kwargs: Any) -> ClientObjectT:
        """Creates an entity and prepares the query"""
        return_type = self.create_typed_object(kwargs, EntityPath(None, self.resource_path))
        self.add_child(return_type)
        qry = CreateEntityQuery(self, return_type, return_type)
        self.context.add_query(qry)
        return return_type

    def create_typed_object(
        self,
        initial_properties: Optional[Dict] = None,
        resource_path: Optional[ResourcePath] = None,
    ) -> ClientObjectT:
        if resource_path is None:
            resource_path = EntityPath(None, self._canonical_collection())
        return super().create_typed_object(initial_properties, resource_path)

    def _canonical_collection(self) -> Optional[ResourcePath]:
        """The collection at which entities of this container are created and addressed.

        Most collections are addressed directly (their own ``resource_path``). A path
        that carries a ``collection`` (OneDrive ``children``, Teams ``joinedTeams`` or
        the Planner owner-scoped collections) instead exposes the canonical top-level
        item set, which is where item CRUD is valid even though listing goes through
        the owner.
        """
        item_path = getattr(self.resource_path, "collection", None)
        return item_path if item_path is not None else self.resource_path

    @property
    def context(self) -> GraphClient:
        from office365.graph_client import GraphClient

        if self._context is None:
            raise ValueError("Graph client is not initialized")
        return cast(GraphClient, self._context)
