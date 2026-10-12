from __future__ import annotations

from office365.delta_collection import DeltaCollection
from office365.planner.buckets.bucket import PlannerBucket
from office365.planner.plans.plan import PlannerPlan
from office365.runtime.odata.literals import escape_odata_string
from office365.runtime.queries.create_entity import CreateEntityQuery


class PlannerBucketCollection(DeltaCollection[PlannerBucket]):
    def __init__(self, context, resource_path=None):
        super().__init__(context, PlannerBucket, resource_path)

    def find_by_name(self, name: str, *, required: bool = False) -> PlannerBucket:
        """Look up a bucket by its ``name``.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        bucket matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            name (str): The bucket name
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"name eq '{escape_odata_string(name)}'", required=required)

    def add(
        self,
        name: str,
        plan: str | PlannerPlan,
    ) -> PlannerBucket:
        """ """
        return_type = PlannerBucket(self.context)
        self.add_child(return_type)
        return_type.name = name

        def _add(plan_id: str | None) -> None:
            assert plan_id is not None
            return_type.plan_id = plan_id
            qry = CreateEntityQuery(self, return_type, return_type)
            self.context.add_query(qry)

        if isinstance(plan, PlannerPlan):
            plan.ensure_property("id").after_execute(lambda _: _add(plan.id))
        else:
            _add(plan)

        return return_type
