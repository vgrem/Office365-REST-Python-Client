from office365.planner.category_descriptions import PlannerCategoryDescriptions
from office365.planner.entity import PlannerEntity
from office365.planner.user_ids import PlannerUserIds
from office365.runtime.types.odata_property import odata


class PlannerPlanDetails(PlannerEntity):
    """
    The plannerPlanDetails resource represents the additional information about a plan.
    Each plan object has a details object.
    """

    @odata(name="categoryDescriptions")
    @property
    def category_descriptions(self) -> PlannerCategoryDescriptions:
        """
        An object that specifies the descriptions of the 25 categories that can be associated with tasks in the plan.
        """
        return self.properties.get("categoryDescriptions", PlannerCategoryDescriptions())

    @category_descriptions.setter
    def category_descriptions(self, value: PlannerCategoryDescriptions) -> None:
        self.set_property("categoryDescriptions", value)

    @odata(name="sharedWith")
    @property
    def shared_with(self) -> PlannerUserIds:
        """
        Set of user IDs that this plan is shared with. If you're using Microsoft 365 groups, use the Groups
        API to manage group membership to share the group's plan. You can also add existing members of the group to
        this collection, although it isn't required for them to access the plan owned by the group.
        """
        return self.properties.get("sharedWith", PlannerUserIds())
