from datetime import datetime, timedelta, timezone

from office365.directory.credential import CredentialExpiryStatus
from office365.directory.key_credential import KeyCredential
from office365.directory.password_credential import PasswordCredential

NOW = datetime.now(timezone.utc)
TEN_DAYS = timedelta(days=10)
EXPECTED_WHOLE_DAYS = 9


def test_unset_end_date():
    for cred in (KeyCredential(), PasswordCredential()):
        assert cred.is_expired is False
        assert cred.days_until_expiry is None


def test_expiry_status_expired():
    status = KeyCredential(endDateTime=NOW.replace(tzinfo=None) - timedelta(days=3)).expiry_status()
    assert status.status is CredentialExpiryStatus.EXPIRED
    assert str(status).startswith("expired ") and str(status).endswith("d ago")
