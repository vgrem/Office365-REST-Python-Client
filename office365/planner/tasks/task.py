from office365.entity import Entity
from office365.planner.tasks.task_details import PlannerTaskDetails
from office365.runtime.paths.resource_path import ResourcePath


class PlannerTask(Entity):
    """
    The plannerTask resource represents a Planner task in Microsoft 365.
    A Planner task is contained in a plan and can be assigned to a bucket in a plan.
    Each task object has a details object which can contain more information about the task.
    See overview for more information regarding relationships between group, plan and task.
    """

    @property
    def title(self):
        """Required. Title of the task."""
        return self.properties.get('title', None)

    @property
    def details(self):
        """Additional details about the task."""
        return self.properties.get('details',
                                   PlannerTaskDetails(self.context, ResourcePath("details", self.resource_path)))
