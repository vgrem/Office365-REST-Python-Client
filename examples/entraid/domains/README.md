# Entra ID Domains

Custom-domain onboarding: add a domain, read the DNS records to create at your
registrar, verify ownership, and set the services the domain is used for.

| What | File | Notes |
|------|------|-------|
| Domain lifecycle | [`manage.py`](./manage.py) | List, add, read verification records, verify, configure services |

```python
domain = client.domains.add(id="contoso-marketing.com").execute_query()
for record in domain.verification_dns_records:
    print(record.record_type, record.label, record.expected_value)
```

## Sharp edges

- **Verification is asynchronous.** Create the DNS record, then call
  `verify()`; propagation can take a while, so a failed verify usually means
  "try again later", not a broken request.
- **A subdomain needs its parent verified first.** Adding `eu.contoso.com`
  requires `contoso.com` to be a verified domain on the tenant.
- **Do not casually edit the initial `.onmicrosoft.com` domain** — it is the
  tenant fallback and is always verified.

---

## API reference

- [domain resource](https://learn.microsoft.com/en-us/graph/api/resources/domain)
