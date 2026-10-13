from __future__ import annotations

from dataclasses import dataclass

from office365.directory.credential import Credential


@dataclass
class KeyCredential(Credential):
    """Contains a key credential (certificate) associated with an application.
    The keyCredentials property of the application entity is a collection of keyCredential.

    Args:
        customKeyIdentifier (str): A 40-character binary type that can be used to identify the credential.
          Optional. When not provided in the payload, defaults to the thumbprint of the certificate.
        displayName (str): Friendly name for the key. Optional.
        endDateTime (datetime.datetime or str): The date and time at which the credential expires.
          The DateTimeOffset type represents date and time information using ISO 8601 format and is always in UTC time
          For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
        key (bytes or str): The certificate's raw data in byte array converted to Base64 string. Returned only on
          $select for a single object, that is, GET applications/{applicationId}?$select=keyCredentials or
          GET servicePrincipals/{servicePrincipalId}?$select=keyCredentials; otherwise, it is always null.
        keyId (str): The unique identifier (GUID) for the key.
        startDateTime (datetime.datetime or): The date and time at which the credential becomes valid.The Timestamp
          type represents date and time information using ISO 8601 format and is always in UTC time. For example,
          midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
        type (str): The type of key credential; for example, Symmetric, AsymmetricX509Cert.
        usage (str): A string that describes the purpose for which the key can be used; for example, Verify.
    """

    customKeyIdentifier: str | None = None
    key: str | None = None
    type: str | None = None
    usage: str | None = None

    @property
    def kind(self) -> str:
        """Human-friendly credential kind label."""
        return "Certificate"

    def __str__(self):
        return self.displayName or "(unnamed)"

    @property
    def entity_type_name(self):
        return "microsoft.graph.KeyCredential"
