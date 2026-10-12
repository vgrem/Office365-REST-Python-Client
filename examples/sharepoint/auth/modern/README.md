# Modern SharePoint authentication

Azure AD / Entra app-only and delegated flows for SharePoint Online. See the
[authentication overview](../README.md) to choose one.

| What | File | Notes |
|------|------|-------|
| App-only with a certificate (PEM) | [`with_certificate.py`](./with_certificate.py) | Recommended for automation |
| App-only with an inline private key | [`with_certificate_and_privkey.py`](./with_certificate_and_privkey.py) | Key from a string |
| App-only with custom scopes | [`with_certificate_and_scopes.py`](./with_certificate_and_scopes.py) | `Sites.Selected` etc. |
| Delegated username & password | [`with_username_and_password.py`](./with_username_and_password.py) | MSAL ROPC (no MFA) |
| Delegated interactive | [`with_interactive.py`](./with_interactive.py) | Browser sign-in |
| Delegated device code | [`with_device_flow.py`](./with_device_flow.py) | Headless / no browser |
| Browser cookies | [`with_cookies.py`](./with_cookies.py) | FedAuth / rtFa |
| Migrate SAML → certificate | [`migrate_from_saml_to_cert.py`](./migrate_from_saml_to_cert.py) | Upgrade guide |
