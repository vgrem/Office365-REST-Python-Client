from office365.entity import Entity


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
