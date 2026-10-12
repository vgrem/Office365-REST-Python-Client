# Legacy SharePoint authentication

Older SharePoint auth flows, kept for on-premises and classic scenarios. Prefer
the modern app-only certificate flow for new work — see the
[authentication overview](../README.md).

> **⚠️ Legacy.** ACS App-Only and SAML user-credential auth are deprecated for
> SharePoint Online. Use them only for on-premises or classic tenants.

| What | File | Notes |
|------|------|-------|
| ACS App-Only principal | [`with_app_only.py`](./with_app_only.py) | Client id + secret |
| User credentials (SAML) | [`with_user_credential.py`](./with_user_credential.py) | Legacy user auth |
| NTLM (on-premises) | [`with_ntlm.py`](./with_ntlm.py) | Windows integrated |
