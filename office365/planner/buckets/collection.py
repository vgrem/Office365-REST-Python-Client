from __future__ import annotations

from typing import Optional, Union

from office365.entity_collection import EntityCollection
from office365.planner.buckets.bucket import PlannerBucket
from office365.planner.internal.paths.collections import PlannerCollectionPath
from office365.planner.plans.plan import PlannerPlan
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.create_entity import CreateEntityQuery


class PlannerBucketCollection(EntityCollection[PlannerBucket]):
    """Buckets of a plan.

    Listed through the owning plan (``/planner/plans/{id}/buckets``) but created and
    addressed at the top-level ``/planner/buckets`` set.
    """

    def __init__(self, context, parent_plan: Optional[PlannerPlan] = None) -> None:
        if parent_plan is None:
            resource_path = ResourcePath("buckets", ResourcePath("planner"))
        else:
            resource_path = PlannerCollectionPath("buckets", parent_plan.resource_path)
        super().__init__(context, PlannerBucket, resource_path, parent_plan)

    def find_by_name(self, name: str, *, required: bool = False) -> PlannerBucket:
        """Look up a bucket by its ``name``.

        Deferred — run with ``execute_query()``. Graph ignores ``$filter`` on a
        plan's buckets (and the top-level ``/planner/buckets`` cannot be listed),
        so the match is made client-side. Tolerant by default: when no bucket
        matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            name (str): The bucket name
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_predicate(lambda b: b.name == name, f"name eq '{name}'", required=required)

    def add(
        self,
        name: str,
        plan: Union[str, PlannerPlan, None] = None,
    ) -> PlannerBucket:
        """Create a new plannerBucket.

        Args:
            name (str): Bucket name
            plan (str|PlannerPlan): Owning plan identifier or object. Optional
                when the collection is already bound to a plan, e.g.
                ``plan.buckets.add("Backlog")``.
        """
        return_type = self.create_typed_object({"name": name})
        self.add_child(return_type)

        def _add(plan_id: Optional[str]) -> None:
            if plan_id is not None:
                return_type.plan_id = plan_id
            self.context.add_query(CreateEntityQuery(PlannerBucketCollection(self.context), return_type, return_type))

        if plan is not None and not isinstance(plan, str):
            plan.ensure_property("id").after_execute(lambda _: _add(plan.id))
        elif isinstance(plan, str):
            _add(plan)
        else:
            owner = self.parent
            if isinstance(owner, PlannerPlan):
                owner.ensure_property("id").after_execute(lambda _: _add(owner.id))
            else:
                _add(None)

        return return_type
