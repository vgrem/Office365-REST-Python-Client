from __future__ import annotations

from datetime import datetime
from typing import Optional

from typing_extensions import Self

from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.planner.buckets.bucket import PlannerBucket
from office365.planner.plans.container import PlannerPlanContainer
from office365.planner.plans.details import PlannerPlanDetails
from office365.planner.tasks.task import PlannerTask
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata


class PlannerPlan(Entity):
    """The plannerPlan resource represents a plan in Microsoft 365. A plan can be owned by a group
    and contains a collection of plannerTasks. It can also have a collection of plannerBuckets.
    Each plan object has a details object that can contain more information about the plan.
    For more information about the relationships between groups, plans, and tasks, see Planner.
    """

    def __str__(self):
        return self.title or self.entity_type_name

    def __repr__(self):
        return self.id or self.entity_type_name

    def delete_object(self, *, ignore_missing: bool = False) -> Self:
        def _construct_request(request: RequestOptions) -> None:
            request.set_header("If-Match", self.properties.get("__etag"))

        return super().delete_object(ignore_missing=ignore_missing).before_execute(_construct_request)

    @property
    def container(self) -> PlannerPlanContainer:
        """Identity of the user, device, or application which created the plan."""
        return self.properties.get("container", PlannerPlanContainer())

    @property
    def title(self) -> Optional[str]:
        """Required. Title of the plan."""
        return self.properties.get("title", None)

    @property
    def buckets(self) -> EntityCollection[PlannerBucket]:
        """Collection of buckets in the plan."""
        return self.properties.get(
            "buckets",
            EntityCollection(
                self.context,
                PlannerBucket,
                ResourcePath("buckets", ResourcePath(self.id, ResourcePath("plans", ResourcePath("planner")))),
            ),
        )

    @property
    def details(self):
        """Additional details about the plan."""
        return self.properties.get(
            "details",
            PlannerPlanDetails(
                self.context,
                ResourcePath("details", ResourcePath(self.id, ResourcePath("plans", ResourcePath("planner")))),
            ),
        )

    @property
    def tasks(self) -> EntityCollection[PlannerTask]:
        """Collection of tasks in the plan."""
        return self.properties.get(
            "tasks",
            EntityCollection(
                self.context,
                PlannerTask,
                ResourcePath("tasks", ResourcePath(self.id, ResourcePath("plans", ResourcePath("planner")))),
            ),
        )

    @odata(name="createdBy")
    @property
    def created_by(self):
        """Identity of the user, device, or application which created the plan."""
        return self.properties.get("createdBy", IdentitySet())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def owner(self) -> Optional[str]:
        """Gets the owner property"""
        return self.properties.get("owner", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerPlan"
