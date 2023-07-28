from office365.directory.security.alerts.alert import Alert
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class Incident(Entity):
    """
    An incident in Microsoft 365 Defender is a collection of correlated alert instances and associated metadata
    that reflects the story of an attack in a tenant.

    Microsoft 365 services and apps create alerts when they detect a suspicious or malicious event or activity.
    Individual alerts provide valuable clues about a completed or ongoing attack. However, attacks typically employ
    various techniques against different types of entities, such as devices, users, and mailboxes. The result is
    multiple alerts for multiple entities in your tenant. Because piecing the individual alerts together to gain
    insight into an attack can be challenging and time-consuming, Microsoft 365 Defender automatically aggregates the
    alerts and their associated information into an incident.
    """

    @property
    def assigned_to(self):
        """Owner of the incident, or null if no owner is assigned. Free editable text.
        :rtype: str or None
        """
        return self.properties.get("assignedTo", None)

    @property
    def alerts(self):
        """The list of related alerts. Supports $expand."""
        return self.properties.get('alerts',
                                   EntityCollection(self.context, Alert, ResourcePath("alerts", self.resource_path)))
