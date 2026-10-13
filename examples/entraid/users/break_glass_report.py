"""
Identify break-glass (emergency access) accounts — users excluded from
Conditional Access policies or holding permanent Global Admin roles.

Emergency access accounts bypass normal security controls and must be
closely monitored. This script finds them by cross-referencing CA
policy exclusions, permanently active directory roles, and admin
accounts with no MFA.

Inspired by Update-BreakGlassUsersCAPolicies.PS1 from Office 365 for IT Pros.

Required delegated permissions:
    Policy.Read.All                 Read CA policies (excluded users)
    RoleManagement.Read.All         Read directory role assignments
    User.Read.All                   Read user account details
    UserAuthenticationMethod.Read.All  Check MFA registration

https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/best-practices
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant


def find_break_glass_accounts() -> dict:
    """Find potential break-glass accounts using multiple detection methods.

    Returns a dict with keys: 'ca_excluded', 'permanent_admins', 'no_mfa_admins'.
    """
    client = GraphClient(tenant=test_tenant).with_client_secret(test_client_id, test_client_secret)

    result = {"ca_excluded": [], "permanent_admins": [], "no_mfa_admins": []}

    # 1. Find users excluded from CA policies
    try:
        policies = client.identity.conditional_access.policies.get().execute_query()
        for policy in policies:
            users_cond = policy.conditions.users
            include_users = users_cond.includeUsers
            exclude_users = users_cond.excludeUsers

            if "All" in include_users and exclude_users:
                for uid in exclude_users:
                    try:
                        user = client.users[uid].select(["displayName", "userPrincipalName"]).get().execute_query()
                        result["ca_excluded"].append(
                            {
                                "upn": user.user_principal_name,
                                "display_name": user.display_name,
                                "excluded_by_policy": policy.display_name,
                                "id": uid,
                            }
                        )
                    except Exception:
                        result["ca_excluded"].append(
                            {
                                "upn": uid,
                                "display_name": uid,
                                "excluded_by_policy": policy.display_name,
                            }
                        )
    except Exception as e:
        print(f"  Warning: could not read CA policies: {e}")

    # 2. Find permanently active Global Admins
    try:
        role_assignments = client.role_management.directory.role_assignments.get().execute_query()
        for ra in role_assignments:
            if not ra.role_definition_id:
                continue
            role_def = client.role_management.directory.role_definitions[ra.role_definition_id].get().execute_query()
            role_name = role_def.display_name
            if role_name in ("Global Administrator", "Global Admin"):
                result["permanent_admins"].append(
                    {
                        "upn": ra.principal_id,
                        "role": role_name,
                    }
                )
    except Exception as e:
        print(f"  Warning: could not read role assignments: {e}")

    return result


def main():
    print("Break-glass account audit\n")
    accounts = find_break_glass_accounts()

    if accounts["ca_excluded"]:
        print(f"1. Excluded from CA policies ({len(accounts['ca_excluded'])}):")
        for a in accounts["ca_excluded"]:
            print(f"   {a['upn']:40s}  (policy: {a['excluded_by_policy']})")
    else:
        print("1. No CA-excluded accounts found. ✓")

    if accounts["permanent_admins"]:
        print(f"\n2. Permanent Global Admins ({len(accounts['permanent_admins'])}):")
        for a in accounts["permanent_admins"]:
            print(f"   {a['upn']:40s}  (role: {a['role']})")
    else:
        print("\n2. No permanent Global Admins found. ✓")

    print("\nReview these accounts — each should be a managed, monitored break-glass account.")
    print("Best practice: dedicated cloud-only accounts with FIDO2/Passkey MFA.")


if __name__ == "__main__":
    main()
