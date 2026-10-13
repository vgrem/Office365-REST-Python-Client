from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from office365.runtime.client_value import ClientValue
from office365.runtime.converters.scalars import ensure_aware_utc

DEFAULT_WARN_DAYS = 30
"""Default threshold (in days) used by :meth:`Credential.expiry_status`."""

_UNSET = datetime.min.replace(tzinfo=timezone.utc)


class CredentialExpiryStatus(Enum):
    """Coarse classification of a credential's remaining validity."""

    NO_EXPIRY = "no expiry"
    VALID = "valid"
    EXPIRING = "expiring"
    EXPIRED = "expired"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CredentialExpiry:
    """Expiry assessment of a credential relative to a ``warn_days`` threshold.

    Returned by :meth:`Credential.expiry_status`. ``status`` is the coarse
    classification and ``days`` the signed number of days left (negative once
    expired, ``None`` when no end date is set). ``str()`` yields a human-friendly
    label such as ``"expires in 10d"``, so the object can be printed directly.
    """

    status: CredentialExpiryStatus
    days: int | None = None

    def __str__(self) -> str:
        if self.status is CredentialExpiryStatus.NO_EXPIRY or self.days is None:
            return "no expiry"
        if self.status is CredentialExpiryStatus.EXPIRED:
            return f"expired {-self.days}d ago"
        if self.status is CredentialExpiryStatus.EXPIRING:
            return f"expiring in {self.days}d"
        return f"expires in {self.days}d"

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)


@dataclass
class Credential(ClientValue):
    """Base class for application/service-principal credentials.

    Holds the fields and expiry semantics shared by client secrets
    (:class:`~office365.directory.password_credential.PasswordCredential`) and
    certificates (:class:`~office365.directory.key_credential.KeyCredential`).
    """

    displayName: str | None = None
    keyId: str | None = None
    startDateTime: datetime = field(default_factory=lambda: datetime.min)
    endDateTime: datetime = field(default_factory=lambda: datetime.min)

    @property
    def is_expired(self) -> bool:
        """True if the credential's end date has passed."""
        end = ensure_aware_utc(self.endDateTime)
        if end is None or end == _UNSET:
            return False
        return end < datetime.now(timezone.utc)

    @property
    def days_until_expiry(self) -> int | None:
        """Signed number of days until expiry, or ``None`` when no end date is set."""
        end = ensure_aware_utc(self.endDateTime)
        if end is None or end == _UNSET:
            return None
        return (end - datetime.now(timezone.utc)).days

    def expiry_status(self, warn_days: int = DEFAULT_WARN_DAYS) -> CredentialExpiry:
        """Classify the credential, flagging one that expires within ``warn_days``.

        Args:
            warn_days: Threshold, in days, below which a still-valid credential
                is reported as :attr:`CredentialExpiryStatus.EXPIRING`.

        Returns:
            CredentialExpiry: A printable status carrying the classification and
                the signed number of days left.
        """
        days = self.days_until_expiry
        if days is None:
            return CredentialExpiry(CredentialExpiryStatus.NO_EXPIRY)
        if self.is_expired:
            return CredentialExpiry(CredentialExpiryStatus.EXPIRED, days)
        status = CredentialExpiryStatus.EXPIRING if days < warn_days else CredentialExpiryStatus.VALID
        return CredentialExpiry(status, days)

    @property
    def kind(self) -> str:
        """Human-friendly credential kind (overridden by concrete subclasses)."""
        return type(self).__name__
