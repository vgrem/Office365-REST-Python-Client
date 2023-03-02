from office365.sharepoint.base_entity import BaseEntity


class WorkflowInstance(BaseEntity):
    """Represents a workflow instance."""

    @property
    def entity_type_name(self):
        return "SP.WorkflowServices.WorkflowInstance"
