from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.planner.buckets.bucket import PlannerBucket
from office365.planner.plans.plan import PlannerPlan
from office365.planner.tasks.task import PlannerTask
from office365.runtime.paths.resource_path import ResourcePath


class Planner(Entity):
    """
    The planner resource is the entry point for the Planner object model.
    It returns a singleton planner resource. It doesn't contain any usable properties.
    """

    @property
    def buckets(self):
        """Read-only. Nullable. Returns the plannerBuckets assigned to the user.

        :rtype: EntityCollection
        """
        return self.get_property('buckets',
                                 EntityCollection(self.context, PlannerBucket,
                                                  ResourcePath("buckets", self.resource_path)))

    @property
    def tasks(self):
        """Read-only. Nullable. Returns the plannerTasks assigned to the user.

        :rtype: EntityCollection
        """
        return self.get_property('tasks',
                                 EntityCollection(self.context, PlannerTask,
                                                  ResourcePath("tasks", self.resource_path)))

    @property
    def plans(self):
        """Read-only. Nullable. Returns the plannerTasks assigned to the user.

        :rtype: EntityCollection
        """
        return self.get_property('plans',
                                 EntityCollection(self.context, PlannerPlan,
                                                  ResourcePath("plans", self.resource_path)))
