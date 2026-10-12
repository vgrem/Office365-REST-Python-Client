from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from office365.entity_collection import EntityCollection
from office365.planner.buckets.bucket import PlannerBucket
from office365.planner.internal.paths.collections import PlannerCollectionPath
from office365.planner.plans.plan import PlannerPlan
from office365.planner.tasks.task import PlannerTask
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.create_entity import CreateEntityQuery

if TYPE_CHECKING:
    from office365.planner.user import PlannerUser


class PlannerTaskCollection(EntityCollection[PlannerTask]):
    """Tasks of a plan, bucket or user.

    Listed through the owning entity (``/planner/plans/{id}/tasks``,
    ``/planner/buckets/{id}/tasks`` or ``/users/{id}/planner/tasks``) but created and
    addressed at the top-level ``/planner/tasks`` set.
    """

    def __init__(self, context, parent: Union[PlannerPlan, PlannerBucket, PlannerUser, None] = None) -> None:
        if parent is None:
            resource_path = ResourcePath("tasks", ResourcePath("planner"))
        else:
            resource_path = PlannerCollectionPath("tasks", parent.resource_path)
        super().__init__(context, PlannerTask, resource_path, parent)

    def _resolve_plan_id(self) -> Optional[str]:
        parent = self.parent
        if isinstance(parent, PlannerBucket):
            return parent.plan_id
        if isinstance(parent, PlannerPlan):
            return parent.id
        return None

    def find_by_title(self, title: str, *, required: bool = False) -> PlannerTask:
        """Look up a task by its ``title``.

        Deferred — run with ``execute_query()``. Graph ignores ``$filter`` when a
        plan's tasks are listed through the plan (and on ``me/planner/tasks``), so
        the match is made client-side. Tolerant by default: when no task matches,
        the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            title (str): The task title
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_predicate(lambda t: t.title == title, f"title eq '{title}'", required=required)

    def add(
        self,
        title: str,
        plan: Union[str, PlannerPlan, None] = None,
        bucket: Union[str, PlannerBucket, None] = None,
    ) -> PlannerTask:
        """Create a new plannerTask.

        Args:
            title (str): Task title
            plan (str|PlannerPlan): Plan identifier or object. Optional when the
                collection is already bound to a plan, e.g. ``plan.tasks.add(...)``.
            bucket (str|PlannerBucket): Bucket identifier or object
        """
        return_type = self.create_typed_object({"title": title})
        self.add_child(return_type)

        def _add(plan_id: Optional[str], bucket_id: Optional[str]) -> None:
            if plan_id is not None:
                return_type.plan_id = plan_id
            if bucket_id is not None:
                return_type.bucket_id = bucket_id
            self.context.add_query(CreateEntityQuery(PlannerTaskCollection(self.context), return_type, return_type))

        def _ensure_plan(bucket_id: Optional[str]) -> None:
            if plan is None:
                _add(self._resolve_plan_id(), bucket_id)
            elif isinstance(plan, str):
                _add(plan, bucket_id)
            else:
                plan_obj = plan
                plan_obj.ensure_property("id").after_execute(lambda _: _add(plan_obj.id, bucket_id))

        if bucket is None:
            _ensure_plan(None)
        elif isinstance(bucket, str):
            _ensure_plan(bucket)
        else:
            bucket.ensure_property("id").after_execute(lambda _: _ensure_plan(bucket.id))

        return return_type
