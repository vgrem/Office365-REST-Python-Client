from __future__ import annotations

from typing import Optional

from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.v4.entity import EntityPath


class PlannerCollectionPath(EntityPath):
    """A Planner collection whose listing is scoped to an owning entity.

    Graph exposes two endpoints per Planner collection:

    * listing is served through the owner, e.g. ``/planner/plans/{id}/buckets`` or
      ``/planner/buckets/{id}/tasks`` (a nested, read-only navigation);
    * each item is created, fetched and updated at the canonical top-level set,
      e.g. ``/planner/buckets/{id}`` or ``/planner/tasks/{id}``.

    The path is lazy: the ``owner`` path is kept as a live reference, so the URL
    resolves once the owner identifier becomes known. The canonical item set is
    carried by the inherited
    :attr:`~office365.runtime.paths.v4.entity.EntityPath.collection` and is used
    whenever an item is created or addressed.
    """

    def __init__(self, segment: str, owner: Optional[ResourcePath]) -> None:
        super().__init__(segment, owner, ResourcePath(segment, ResourcePath("planner")))
