from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.workflowservices.instance import WorkflowInstance


class WorkflowInstanceService(BaseEntity):
    """Manages and reads workflow instances from the workflow host."""

    def enumerate_instances_for_site(self):
        """
        Returns the site workflow instances for the current site.
        """
        return_type = BaseEntityCollection(self.context, WorkflowInstance)
        qry = ServiceOperationQuery(self, "EnumerateInstancesForSite", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "SP.WorkflowServices.WorkflowInstanceService"
