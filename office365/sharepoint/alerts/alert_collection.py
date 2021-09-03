from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.alerts.alert import Alert
from office365.sharepoint.base_entity_collection import BaseEntityCollection


class AlertCollection(BaseEntityCollection):
    """Content Type resource collection"""

    def __init__(self, context, resource_path=None):
        super(AlertCollection, self).__init__(context, Alert, resource_path)

    def add(self, parameters):
        """

        :type parameters: office365.sharepoint.alerts.alert_creation_information.AlertCreationInformation
        """
        alert = Alert(self.context, None)
        self.add_child(alert)
        qry = ServiceOperationQuery(self, "Add", None, parameters, "alertCreationInformation", alert)
        self.context.add_query(qry)
        return alert

    def contains(self, id_alert):
        """
        :param str id_alert:
        """
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "Contains", {"idAlert": id_alert}, None, None, return_type)
        self.context.add_query(qry)
        return return_type
