# Entra ID Users

User lifecycle and reporting: create, update, disable and restore accounts;
manage passwords, managers, groups and licenses; invite guests (B2B); and run the
reports that answer "who is inactive, who lacks MFA, and who still has access".

Read-only scripts use an app-only client or a delegated sign-in as noted per
script; writes use delegated or interactive sign-in.

## 1. Lifecycle

| What | File | Notes |
|------|------|-------|
| Create a user | [`create.py`](./create.py) | Set UPN, display name, password |
| Update a profile | [`update.py`](./update.py) | Job title, department, etc. |
| Bulk update | [`update_batch.py`](./update_batch.py) | Batch requests in one round trip |
| Delete a user | [`delete.py`](./delete.py) | Soft-delete (restorable for 30 days) |
| Restore a deleted user | [`restore_deleted_user.py`](./restore_deleted_user.py) | From `directory/deletedItems` |
| Import from CSV | [`import.py`](./import.py) | Row-by-row create |
| Import users from CSV (helper) | [`import_users_csv.py`](./import_users_csv.py) | Uses the CSV import helper |

## 2. Read and export

| What | File | Notes |
|------|------|-------|
| Count users | [`get_count.py`](./get_count.py) | `count()` without paging |
| Disabled accounts | [`get_disabled.py`](./get_disabled.py) | `accountEnabled eq false` |
| Export to CSV | [`export.py`](./export.py) | Streams all users to a file |
| Export to a dataframe | [`export_dataframe.py`](./export_dataframe.py) | Returns a `pandas.DataFrame` |
| Export personal data (GDPR) | [`export_personal_data.py`](./export_personal_data.py) | `exportPersonalData` job |
| A user's group memberships | [`get_group_memberships.py`](./get_group_memberships.py) | `memberOf`, transited |
| A user's app role assignments | [`list_app_role_assignments.py`](./list_app_role_assignments.py) | Enterprise-app roles |
| A user's recent activity | [`get_my_activities.py`](./get_my_activities.py) | Activity feed |

## 3. Passwords and managers

| What | File | Notes |
|------|------|-------|
| Reset a password | [`reset_password.py`](./reset_password.py) | Force change at next sign-in |
| Users with expired passwords | [`password_expiry_report.py`](./password_expiry_report.py) | `passwordPolicies` based |
| Assign a manager | [`assign_manager.py`](./assign_manager.py) | `$ref` to the manager |
| Get a user's manager | [`get_manager.py`](./get_manager.py) | |

## 4. Guests (B2B)

| What | File | Notes |
|------|------|-------|
| Invite a guest | [`invite_guest.py`](./invite_guest.py) | Sends the invitation email |
| Inactive guests | [`find_inactive_guests.py`](./find_inactive_guests.py) | Guests with no recent sign-in |
| Remove inactive accounts | [`remove_inactive_accounts.py`](./remove_inactive_accounts.py) | Two-phase: disable first, delete on a later run |

## 5. Authentication and MFA

| What | File | Notes |
|------|------|-------|
| Registered auth methods | [`auth_methods.py`](./auth_methods.py) | FIDO2, phone, Authenticator per user |
| Disable MFA for a user | [`disable_mfa.py`](./disable_mfa.py) | Clears registered methods |
| MFA readiness report | [`mfa_status_report.py`](./mfa_status_report.py) | Users without strong auth |
| Break-glass account audit | [`break_glass_report.py`](./break_glass_report.py) | CA exclusions and permanent admins |

## 6. Reporting recipes

| What | File | Notes |
|------|------|-------|
| Full user report | [`report.py`](./report.py) | Sign-in activity, inactivity, MFA |
| Last sign-in report | [`last_signin_report.py`](./last_signin_report.py) | `signInActivity` |
| Privileged users | [`../roles/privileged_users.py`](../roles/privileged_users.py) | Inverted view: per user, every admin role |

## Sharp edges

- **Deleting a user is a soft delete.** The object moves to
  `directory/deletedItems` for 30 days and `restore_deleted_user.py` can bring it
  back; permanent deletion is a separate flow.
- **`signInActivity` needs `AuditLog.Read.All`** and is only populated for
  licensed users; recently created accounts legitimately show no data.
- **Guest invitations create a redeemed-or-pending user object.** Filter on
  `userType eq 'Guest'` and check `externalUserState` before treating one as
  active.

---

## API reference

- [user resource](https://learn.microsoft.com/en-us/graph/api/resources/user)
- [invitation (B2B)](https://learn.microsoft.com/en-us/graph/api/resources/invitation)
- [authentication methods overview](https://learn.microsoft.com/en-us/graph/api/resources/authenticationmethods-overview)
