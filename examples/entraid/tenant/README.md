# Entra ID Tenant

Tenant-wide configuration: the organization profile, branding, and partner
relationships.

| What | File | Notes |
|------|------|-------|
| Organization settings | [`organization.py`](./organization.py) | Profile, verified domains, branding, partner relationships |

```python
org = client.organization.get().execute_query()[0]
print(org.display_name, org.tenant_type, org.verified_domains)
```

## Sharp edges

- **`client.organization` is a singleton collection.** Read `[0]`; do not expect
  multiple organizations unless the signed-in identity is a multi-tenant guest.
- **Branding updates need `Organization.ReadWrite.All`**; the read-only profile
  works with `Organization.Read.All`.

---

## API reference

- [organization resource](https://learn.microsoft.com/en-us/graph/api/resources/organization)
