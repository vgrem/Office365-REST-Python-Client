from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from office365.runtime.client_value import ClientValue
from office365.subscriptions.encrypted_content import ChangeNotificationEncryptedContent
from office365.subscriptions.lifecycleeventtype import LifecycleEventType
from office365.subscriptions.resource_data import ResourceData


@dataclass
class ChangeNotification(ClientValue):
    """Represents the notification sent to the subscriber.

    Args:
        changeType (str): Indicates the type of change that will raise the change notification. The supported values
          are: created, updated, deleted. Required.
        clientState (str): Value of the clientState property sent in the subscription request (if any).
          The maximum length is 255 characters. The client can check whether the change notification came from the
          service by comparing the values of the clientState property. The value of the clientState property sent with
          the subscription is compared with the value of the clientState property received with each change notification.
        encryptedContent (ChangeNotificationEncryptedContent): Encrypted content attached with the change notification.
          Only provided if encryptionCertificate and includeResourceData were defined during the subscription request
          and if the resource supports it. Optional.
        resource (str): The URI of the resource that emitted the change notification relative to
          https://graph.microsoft.com. Required
        resourceData (ResourceData): The content of this property depends on the type of resource being subscribed to.
    """

    changeType: str | None = None
    clientState: str | None = None
    encryptedContent: ChangeNotificationEncryptedContent = field(default_factory=ChangeNotificationEncryptedContent)
    resource: str | None = None
    resourceData: ResourceData = field(default_factory=ResourceData)

    id: str | None = None

    lifecycleEvent: LifecycleEventType = LifecycleEventType.missed

    subscriptionExpirationDateTime: datetime | None = None

    subscriptionId: UUID | None = None

    tenantId: UUID | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ChangeNotification"
