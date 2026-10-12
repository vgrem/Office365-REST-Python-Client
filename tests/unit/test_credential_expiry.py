from datetime import datetime, timedelta, timezone

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
