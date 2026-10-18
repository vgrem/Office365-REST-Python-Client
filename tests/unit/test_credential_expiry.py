from datetime import datetime, timedelta, timezone

from office365.directory.credential import CredentialExpiryStatus
from office365.directory.key_credential import KeyCredential
from office365.directory.password_credential import PasswordCredential

NOW = datetime.now(timezone.utc)
TEN_DAYS = timedelta(days=10)
EXPECTED_WHOLE_DAYS = 9


def test_naive_end_date_is_treated_as_utc():
    """Locally created credentials carry naive dates; expiry maths must not raise."""
    cred = KeyCredential(endDateTime=NOW.replace(tzinfo=None) + TEN_DAYS)
    assert cred.is_expired is False
    assert cred.days_until_expiry == EXPECTED_WHOLE_DAYS


def test_aware_end_date_is_supported():
    cred = PasswordCredential(endDateTime=NOW + TEN_DAYS)
    assert cred.is_expired is False
    assert cred.days_until_expiry == EXPECTED_WHOLE_DAYS


def test_expired_credential():
    cred = KeyCredential(endDateTime=NOW.replace(tzinfo=None) - timedelta(days=3))
    assert cred.is_expired is True
    assert cred.days_until_expiry is not None and cred.days_until_expiry < 0


def test_unset_end_date():
    for cred in (KeyCredential(), PasswordCredential()):
        assert cred.is_expired is False
        assert cred.days_until_expiry is None


def test_none_end_date():
    for cred in (KeyCredential(endDateTime=None), PasswordCredential(endDateTime=None)):
        assert cred.is_expired is False
        assert cred.days_until_expiry is None


def test_expiry_status_classifies_relative_to_warn_days():
    cred = KeyCredential(endDateTime=NOW + TEN_DAYS)
    assert cred.expiry_status(warn_days=30).status is CredentialExpiryStatus.EXPIRING
    assert cred.expiry_status(warn_days=5).status is CredentialExpiryStatus.VALID


def test_expiry_status_label_is_printable_and_formattable():
    status = KeyCredential(endDateTime=NOW + TEN_DAYS).expiry_status(warn_days=30)
    assert str(status) == "expiring in 9d"
    assert f"{status:<16}" == "expiring in 9d".ljust(16)


def test_expiry_status_expired():
    status = KeyCredential(endDateTime=NOW.replace(tzinfo=None) - timedelta(days=3)).expiry_status()
    assert status.status is CredentialExpiryStatus.EXPIRED
    assert str(status).startswith("expired ") and str(status).endswith("d ago")


def test_expiry_status_without_end_date():
    for cred in (KeyCredential(), PasswordCredential()):
        status = cred.expiry_status()
        assert status.status is CredentialExpiryStatus.NO_EXPIRY
        assert str(status) == "no expiry"


def test_credential_kind_labels():
    assert KeyCredential().kind == "Certificate"
    assert PasswordCredential().kind == "Password"
