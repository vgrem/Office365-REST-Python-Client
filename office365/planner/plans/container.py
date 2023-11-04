from office365.runtime.client_value import ClientValue


class PlannerPlanContainer(ClientValue):
    """
    Represents a container for a plannerPlan. The container is a resource that specifies authorization rules and the
    lifetime of the plan. This means that only the people who are authorized to work with the resource containing
    the plan will be able to work with the plan and the tasks within it. When the containing resource is deleted,
    the contained plans are also deleted. The properties of the plannerPlanContainer cannot be changed after the plan
    is created.
    """
