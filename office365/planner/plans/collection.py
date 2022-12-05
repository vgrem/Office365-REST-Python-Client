from office365.directory.users.user import User
from office365.entity_collection import EntityCollection
from office365.planner.plans.plan import PlannerPlan
from office365.runtime.queries.create_entity import CreateEntityQuery


class PlannerPlanCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(PlannerPlanCollection, self).__init__(context, PlannerPlan, resource_path)

    def add(self, title, owner=None):
        """
        Creates a new plannerPlan.

        :param str title: Planner name
        :param str or office365.directory.users.user.User owner: Planner owner
        """
        return_type = PlannerPlan(self.context)
        self.add_child(return_type)

        def _create_query(owner_id):
            payload = {
                "title": title,
                "owner": {"@odata.id": "https://graph.microsoft.com/v1.0/users/{0}".format(owner_id)}
            }
            return CreateEntityQuery(self, payload, return_type)

        if isinstance(owner, User):
            def _owner_loaded():
                next_qry = _create_query(owner.id)
                self.context.add_query(next_qry)
            owner.ensure_property("id", _owner_loaded)
        else:
            qry = _create_query(owner)
            self.context.add_query(qry)

        return return_type

