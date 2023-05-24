from office365.directory.security.alerts.evidence import AlertEvidence
from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection


class Alert(Entity):
    """This resource corresponds to the latest generation of alerts in the Microsoft Graph security API,
    representing potential security issues within a customer's tenant that Microsoft 365 Defender,
    or a security provider integrated with Microsoft 365 Defender, has identified."""

    @property
    def evidence(self):
        """Collection of evidence related to the alert."""
        return self.properties.get("evidence", ClientValueCollection(AlertEvidence))
