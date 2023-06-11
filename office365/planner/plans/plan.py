from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.planner.buckets.bucket import PlannerBucket
from office365.planner.plans.plan_details import PlannerPlanDetails
from office365.planner.tasks.task import PlannerTask
from office365.runtime.paths.resource_path import ResourcePath


class PlannerPlan(Entity):
    """The plannerPlan resource represents a plan in Microsoft 365. A plan can be owned by a group
    and contains a collection of plannerTasks. It can also have a collection of plannerBuckets.
    Each plan object has a details object that can contain more information about the plan.
    For more information about the relationships between groups, plans, and tasks, see Planner.
    """

    @property
    def title(self):
        """Required. Title of the plan."""
        return self.properties.get('title', None)

    @property
    def created_by(self):
        """Identity of the user, device, or application which created the plan."""
        return self.properties.get('createdBy', IdentitySet())

    @property
    def buckets(self):
        """
        Read-only. Nullable. Collection of buckets in the plan.
        """
        return self.properties.get('buckets',
                                   EntityCollection(self.context, PlannerBucket,
                                                    ResourcePath("buckets", self.resource_path)))

    @property
    def details(self):
        """
        Read-only. Nullable. Additional details about the plan.
        """
        return self.properties.get('details',
                                   PlannerPlanDetails(self.context, ResourcePath("details", self.resource_path)))

    @property
    def tasks(self):
        """
        Read-only. Nullable. Collection of tasks in the plan.
        """
        return self.properties.get('tasks',
                                   EntityCollection(self.context, PlannerTask,
                                                    ResourcePath("tasks", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "createdBy": self.created_by,
            }
            default_value = property_mapping.get(name, None)
        return super(PlannerPlan, self).get_property(name, default_value)
