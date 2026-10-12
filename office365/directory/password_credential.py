from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from office365.runtime.client_value import ClientValue
from office365.runtime.converters.scalars import ensure_aware_utc


@dataclass
class PasswordCredential(ClientValue):
    """Represents a password credential associated with an application or a service principal.
    The passwordCredentials property of the application entity is a collection of passwordCredential objects.
    """

    displayName: str | None = None
    secretText: str | None = None
    keyId: str | None = None
    startDateTime: datetime = field(default_factory=lambda: datetime.min)
    endDateTime: datetime = field(default_factory=lambda: datetime.min)
    customKeyIdentifier: bytes | None = None
    hint: str | None = None

    @property
    def is_expired(self) -> bool:
        """True if the credential's end date has passed."""
        end = ensure_aware_utc(self.endDateTime)
        if end is None or end == datetime.min.replace(tzinfo=timezone.utc):
            return False
        return end < datetime.now(timezone.utc)

    @property
    def days_until_expiry(self) -> int | None:
        """Number of days until expiry, or None if no end date is set."""
        end = ensure_aware_utc(self.endDateTime)
        if end is None or end == datetime.min.replace(tzinfo=timezone.utc):
            return None
        return (end - datetime.now(timezone.utc)).days

    def __str__(self):
        return str(self.displayName or self.entity_type_name or "")

    @property
    def entity_type_name(self):
        return None
