from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class InformationRightsManagementFileSettings(BaseEntity):
    """Represents the Information Rights Management (IRM) settings of a file."""

    def reset(self):
        """Resets all properties to the default value."""
        qry = ServiceOperationQuery(self, "Reset")
        self.context.add_query(qry)
        return self
