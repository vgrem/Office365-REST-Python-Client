"""
Report on users without multi-factor authentication (MFA) registered.

Identifies users who have not enrolled in MFA — a critical security
gap. Checks authentication methods (phone, authenticator app, FIDO2)
to determine MFA readiness.

Inspired by ReportMFAStatusUsers.PS1 and ReportMFAStatusAdmins.PS1
from Office 365 for IT Pros.

Required delegated permissions:
    User.Read.All                   Read user profiles
    UserAuthenticationMethod.Read.All  Read authentication methods
    Directory.Read.All              (optional) check admin roles

https://learn.microsoft.com/en-us/graph/api/resources/authenticationmethods-overview
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

STRONG_METHODS = {
    "microsoft.graph.MicrosoftAuthenticatorAuthenticationMethod",
    "microsoft.graph.PhoneAuthenticationMethod",
    "microsoft.graph.Fido2AuthenticationMethod",
    "microsoft.graph.WindowsHelloForBusinessAuthenticationMethod",
    "microsoft.graph.PasswordlessMicrosoftAuthenticatorAuthenticationMethod",
}

_DISPLAY_LIMIT = 20


def user_has_mfa(client: GraphClient, user_id: str | None) -> bool:
    """Check if a user has at least one strong MFA method registered."""
    if not user_id:
        return False
    try:
        methods = client.users[user_id].authentication.methods.get().execute_query()
        for method in methods:
            if method.entity_type_name in STRONG_METHODS:
                return True
    except Exception:
        pass
    return False


def mfa_status_report() -> tuple[list[dict], list[dict]]:
    """Check MFA registration status for all users.

    Returns:
        Tuple of (users_with_mfa, users_without_mfa).
    """
    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    with_mfa = []
    without_mfa = []

    users = client.users.get_all().execute_query()
    for user in users:
        has = user_has_mfa(client, user.id)
        entry = {
            "upn": user.user_principal_name,
            "display_name": user.display_name,
            "user_type": user.user_type,
        }
        if has:
            with_mfa.append(entry)
        else:
            without_mfa.append(entry)

    return with_mfa, without_mfa


def main():
    print("Checking MFA registration status for all users...\n")
    with_mfa, without_mfa = mfa_status_report()

    total = len(with_mfa) + len(without_mfa)
    print(f"Total users: {total}")
    print(f"MFA registered: {len(with_mfa)} ({len(with_mfa) / total * 100:.0f}%)")
    print(f"No MFA:        {len(without_mfa)} ({len(without_mfa) / total * 100:.0f}%)")

    if without_mfa:
        print(f"\nUsers without MFA ({len(without_mfa)}):\n")
        for u in without_mfa[:_DISPLAY_LIMIT]:
            print(f"  {u['upn']:45s}  {u['display_name'][:30]}")
        if len(without_mfa) > _DISPLAY_LIMIT:
            print(f"\n  ... and {len(without_mfa) - _DISPLAY_LIMIT} more")


if __name__ == "__main__":
    main()
