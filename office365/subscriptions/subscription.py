from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from office365.entity import Entity
from office365.runtime.converters.scalars import iso_z, parse_datetime
from office365.runtime.odata.json_format import ODataJsonFormat
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata


class Subscription(Entity):
    """A subscription allows a client app to receive change notifications about changes to data in Microsoft Graph"""

    def reauthorize(self):
        """Reauthorize a subscription when you receive a reauthorizationRequired challenge."""
        qry = ServiceOperationQuery(self, "reauthorize")
        self.context.add_query(qry)
        return self

    @property
    def application_id(self) -> Optional[str]:
        """
        Identifier of the application used to create the subscription.
        """
        return self.properties.get("applicationId", None)

    @property
    def change_type(self) -> Optional[str]:
        """
        Required. Indicates the type of change in the subscribed resource that will raise a change notification.
        The supported values are: created, updated, deleted.
        Multiple values can be combined using a comma-separated list.

        Note:
        Drive root item and list change notifications support only the updated changeType.
        User and group change notifications support updated and deleted changeType. Use updated to receive
        notifications when user or group is created, updated or soft deleted. Use deleted to receive notifications
        when user or group is permanently deleted.
        """
        return self.properties.get("changeType", None)

    @property
    def client_state(self) -> Optional[str]:
        """
        Required. Specifies the value of the clientState property sent by the service in each change notification.
        The maximum length is 128 characters. The client can check that the change notification came from the service
        by comparing the value of the clientState property sent with the subscription with the value of the clientState
        property received with each change notification.
        """
        return self.properties.get("clientState", None)

    @property
    def creator_id(self) -> Optional[str]:
        """
        Optional. Identifier of the user or service principal that created the subscription. If the app used
        delegated permissions to create the subscription, this field contains the id of the signed-in user the app
        called on behalf of. If the app used application permissions, this field contains the id of the service
        principal corresponding to the app. Read-only.
        """
        return self.properties.get("creatorId", None)

    @property
    def encryption_certificate(self) -> Optional[str]:
        """
        Optional. A base64-encoded representation of a certificate with a public key used to encrypt resource data in
        change notifications. Optional but required when includeResourceData is true.
        """
        return self.properties.get("encryptionCertificate", None)

    @property
    def encryption_certificate_id(self) -> Optional[str]:
        """
        Optional. A custom app-provided identifier to help identify the certificate needed to decrypt resource data.
        """
        return self.properties.get("encryptionCertificateId", None)

    @odata(name="expirationDateTime")
    @property
    def expiration_datetime(self) -> Optional[datetime]:
        """
        Required. Specifies the date and time when the webhook subscription expires. The time is in UTC, and can be
        an amount of time from subscription creation that varies for the resource subscribed to
        """
        return self.properties.get("expirationDateTime", datetime.min)

    @expiration_datetime.setter
    def expiration_datetime(self, value: Union[datetime, str]) -> None:
        """Set the subscription expiry."""
        self.set_property("expirationDateTime", value)

    def to_json(self, json_format: Optional[ODataJsonFormat] = None) -> Dict[str, Any] | List[Any]:
        """Serialize the subscription, emitting ``expirationDateTime`` as UTC ``Z``.

        Microsoft Graph subscriptions expect a UTC timestamp ending in ``Z``;
        the generic datetime serializer would otherwise emit a numeric offset
        (``+00:00``), which some endpoints reject.
        """
        payload = super().to_json(json_format)
        if isinstance(payload, dict):
            expiration = payload.get("expirationDateTime")
            if isinstance(expiration, datetime):
                payload["expirationDateTime"] = iso_z(expiration)
            elif isinstance(expiration, str):
                parsed = parse_datetime(expiration)
                if parsed is not None:
                    payload["expirationDateTime"] = iso_z(parsed)
        return payload

    @property
    def include_resource_data(self) -> Optional[bool]:
        """
        Optional. When set to true, change notifications include resource data (such as content of a chat message).
        """
        return self.properties.get("includeResourceData", None)

    @property
    def latest_supported_tls_version(self) -> Optional[str]:
        """
        Optional. Specifies the latest version of Transport Layer Security (TLS) that the notification endpoint,
        specified by notificationUrl, supports. The possible values are: v1_0, v1_1, v1_2, v1_3.

        For subscribers whose notification endpoint supports a version lower than the currently recommended
        version (TLS 1.2), specifying this property by a set timeline allows them to temporarily use their deprecated
        version of TLS before completing their upgrade to TLS 1.2. For these subscribers, not setting this property
        per the timeline would result in subscription operations failing.

        For subscribers whose notification endpoint already supports TLS 1.2, setting this property is optional.
        In such cases, Microsoft Graph defaults the property to v1_2.
        """
        return self.properties.get("latestSupportedTlsVersion", None)

    @property
    def lifecycle_notification_url(self) -> Optional[str]:
        """
        Required for Teams resources if the expirationDateTime value is more than 1 hour from now; optional otherwise.
        The URL of the endpoint that receives lifecycle notifications, including subscriptionRemoved,
        reauthorizationRequired, and missed notifications. This URL must make use of the HTTPS protocol.
        For more information, see Reduce missing subscriptions and change notifications.
        """
        return self.properties.get("lifecycleNotificationUrl", None)

    @property
    def notification_url(self) -> Optional[str]:
        """
        Required. The URL of the endpoint that will receive the change notifications. This URL must make use of
        the HTTPS protocol. Any query string parameter included in the notificationUrl property will be included
        in the HTTP POST request when Microsoft Graph sends the change notifications.
        """
        return self.properties.get("notificationUrl", None)

    @property
    def resource(self) -> Optional[str]:
        """
        Specifies the resource that will be monitored for changes.
        Do not include the base URL (https://graph.microsoft.com/v1.0/). See the possible resource path values for
        each supported resource.
        """
        return self.properties.get("resource", None)

    @property
    def notification_query_options(self) -> Optional[str]:
        """Gets the notificationQueryOptions property"""
        return self.properties.get("notificationQueryOptions", None)

    @property
    def notification_url_app_id(self) -> Optional[str]:
        """Gets the notificationUrlAppId property"""
        return self.properties.get("notificationUrlAppId", None)

    @property
    def vapid_public_key(self) -> Optional[str]:
        """Gets the vapidPublicKey property"""
        return self.properties.get("vapidPublicKey", None)

    @property
    def web_push_encryption_p256dh_public_key(self) -> Optional[str]:
        """Gets the webPushEncryptionP256dhPublicKey property"""
        return self.properties.get("webPushEncryptionP256dhPublicKey", None)

    @property
    def web_push_encryption_secret(self) -> Optional[str]:
        """Gets the webPushEncryptionSecret property"""
        return self.properties.get("webPushEncryptionSecret", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Subscription"
