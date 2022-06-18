from office365.entity import Entity
from office365.runtime.queries.service_operation import ServiceOperationQuery


class UserTeamwork(Entity):
    """A container for the range of Microsoft Teams functionalities that are available per user in the tenant."""

    def send_activity_notification(self, topic, activity_type, chain_id, preview_text, template_parameters):
        payload = {
            "topic": topic,
            "activityType": activity_type,
            "chainId": chain_id,
            "previewText": preview_text,
            "templateParameters": template_parameters,
        }
        qry = ServiceOperationQuery(self, "sendActivityNotification", None, payload)
        self.context.add_query(qry)
        return self
