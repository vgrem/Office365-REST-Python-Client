# Entra ID Directory Roles

Manage Entra ID (Azure AD) directory roles — list activated roles, see who
holds them, assign/remove members, and report on privileged assignments.

> **Directory roles vs unified roles:** the `directory_roles` API covers the
> system-defined **administrator roles** (Global Administrator, Security
> Administrator, …). `role_management.directory` covers the **unified role
> definitions/assignments** used by PIM and custom roles.

---

## Prerequisites

| Role | Required to |
|---|---|
| **Global Administrator** or **Privileged Role Administrator** | Assign, activate, or remove roles |
| **Global Reader** | List roles and their members |

| Permission | Description | Reference |
|---|---|---|
| `RoleManagement.Read.Directory` | List roles and members | [RoleManagement permissions](https://learn.microsoft.com/en-us/graph/permissions-reference#rolemanagement-permissions) |
| `RoleManagement.ReadWrite.Directory` | Assign/remove role members | [RoleManagement permissions](https://learn.microsoft.com/en-us/graph/permissions-reference#rolemanagement-permissions) |
| `RoleManagement.Read.All` | PIM role assignments | [RoleManagement permissions](https://learn.microsoft.com/en-us/graph/permissions-reference#rolemanagement-permissions) |

---

## Examples

| Operation | File | Permission | API |
|---|---|---|---|
| List activated directory roles | [`list.py`](./list.py) | `RoleManagement.Read.Directory` | [directoryRole list](https://learn.microsoft.com/en-us/graph/api/directoryrole-list) |
| List members of a role | [`list_role_members.py`](./list_role_members.py) | `RoleManagement.Read.Directory` | [directoryRole list members](https://learn.microsoft.com/en-us/graph/api/directoryrole-list-members) |
| Roles for the current user | [`for_current_user.py`](./for_current_user.py) | `RoleManagement.Read.Directory` | [user memberOf](https://learn.microsoft.com/en-us/graph/api/user-list-memberof) |
| Roles for a specific user | [`for_user.py`](./for_user.py) | `RoleManagement.Read.Directory` | [user memberOf](https://learn.microsoft.com/en-us/graph/api/user-list-memberof) |
| Assign a role to a user | [`assign_role.py`](./assign_role.py) | `RoleManagement.ReadWrite.Directory` | [directoryRole add member](https://learn.microsoft.com/en-us/graph/api/directoryrole-post-members) |
| Remove a user from a role | [`remove_role.py`](./remove_role.py) | `RoleManagement.ReadWrite.Directory` | [directoryRole delete member](https://learn.microsoft.com/en-us/graph/api/directoryrole-delete-member) |
| PIM role assignments report | [`pim_report.py`](./pim_report.py) | `RoleManagement.Read.All` | [roleAssignment list](https://learn.microsoft.com/en-us/graph/api/rbacapplication-list-roleassignments) |
| Privileged users — who holds which admin role | [`privileged_users.py`](./privileged_users.py) | `Directory.Read.All` | [directoryRole list members](https://learn.microsoft.com/en-us/graph/api/directoryrole-list-members) |

---

## Notes

- **Roles must be activated before they appear in `directory_roles`.** The
  `assign_role.py` example activates a role (idempotently) before assigning.
  `remove_role.py`/`list_role_members.py` operate on already-activated roles.
- **PIM** (`pim_report.py`) reads *eligible* and *active* assignments through
  `role_management.directory`, which covers both built-in and custom roles.

---

## API reference

- [directoryRole resource](https://learn.microsoft.com/en-us/graph/api/resources/directoryrole)
- [roleDefinition / roleAssignment (unified)](https://learn.microsoft.com/en-us/graph/api/resources/unifiedroleassignment)
