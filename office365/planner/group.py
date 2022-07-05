from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.planner.plans.plan import PlannerPlan
from office365.runtime.paths.resource_path import ResourcePath


class PlannerGroup(Entity):
    """
    The plannerGroup resource provides access to Planner resources for a group.
    It doesn't contain any usable properties.
    """

    @property
    def plans(self):
        """Read-only. Nullable. Returns the plannerPlans owned by the group.

        :rtype: EntityCollection
        """
        return self.get_property('plans',
                                 EntityCollection(self.context, PlannerPlan, ResourcePath("plans", self.resource_path)))
