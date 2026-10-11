# Microsoft Purview

Compliance and information protection for Microsoft 365: eDiscovery cases,
retention labels, sensitivity labels, subject rights requests, and threat
assessment.

Purview is a *product* whose entire API surface lives under the Graph
`/security` endpoint (plus `/informationProtection` for threat assessment). The
[security examples](../security/) call the same `client.security` root — that
folder covers Microsoft Defender XDR, this one covers Purview. Same API,
different audience: a compliance/records administrator here, a security analyst
there.

---

## Start here

### [Quickstart — capability snapshot](quickstart.py)

Purview is really a family of services with **separate permissions and, in some
cases, separate administrator roles**. Before anything else, find out which
surfaces your tenant actually exposes: the quickstart probes each one and prints
`OK`, `DENIED` (which permission is missing), or `BLOCKED` (the service is not
provisioned).

```bash
python quickstart.py
```

```text
  OK       Threat assessments       10 object(s)
  DENIED   eDiscovery cases         ... grant eDiscovery.ReadWrite.All
  BLOCKED  Retention labels         UnknownError: Unauthorized (needs Compliance Administrator)
```

It is read-only and never raises on a denial, so it is safe to run anywhere.

!!! note "Guards vs. errors"
    The examples layer two mechanisms, on purpose:

    * a **pre-flight guard** (`require_role`, `require_delegated_permission`, …)
      checks a hard prerequisite *before* the first call and exits **1** — a
      configuration problem the operator must fix;
    * a **typed `AccessDeniedException`** catch handles a per-call denial at
      runtime and exits **0** with a hint — the script did its job, the service
      said no.

    Which one leads depends on the failure the service produces. Records and
    sensitivity labels need an administrator role and answer a missing role with
    an opaque *Unauthorized*, so those scripts **guard** with `require_role`;
    threat assessment **guards** with `require_delegated_permission`; the
    app-only eDiscovery and subject-rights scripts **catch**, because the denial
    message is already precise and the first call is the only side effect.

    Threat assessment is the one script in this folder verified against a live
    tenant; the rest are correct against the API but gated by the permissions
    above.

---

## The Purview surfaces

| Folder | What it answers |
| --- | --- |
| [ediscovery](ediscovery/README.md) | How do I collect and review content for an investigation? |
| [records](records/README.md) | How long do I keep content, and what happens at the end? |
| [sensitivity-labels](sensitivity-labels/README.md) | How is content classified by confidentiality? |
| [subject-rights](subject-rights/README.md) | How do I track GDPR/CCPA data subject requests? |
| [threat-assessment](threat-assessment/README.md) | Is this URL or file phishing/malware? |

---

## Permissions at a glance

| Surface | Permission | Auth | Extra prerequisite |
| --- | --- | --- | --- |
| eDiscovery | `eDiscovery.ReadWrite.All` | app-only | — |
| Records management | `RecordsManagement.ReadWrite.All` | delegated | Compliance Administrator role |
| Sensitivity labels | `InformationProtectionPolicy.Read.All` | delegated | Compliance Administrator role |
| Subject rights | `SubjectRightsRequest.ReadWrite.All` | app-only | service must be provisioned |
| Threat assessment | `ThreatAssessment.ReadWrite.All` | delegated | — |

!!! warning "Records and sensitivity labels are delegated-only"
    The records and information-protection APIs do **not** support app-only
    access on this generation of the API: they need an interactive sign-in by a
    user holding the Compliance Administrator (or Global Administrator) role,
    which is why those examples use `with_token_interactive`.

---

## Related examples

- Apply a sensitivity label to a SharePoint file — [`../sharepoint/sites/assign_sensitivity_label.py`](../sharepoint/sites/assign_sensitivity_label.py)
- Publish and apply retention labels in SharePoint — [`../sharepoint/compliance/`](../sharepoint/compliance/)
- Microsoft Defender XDR (alerts, incidents, hunting, secure score) — [`../security/`](../security/)
- File / email-file threat assessments in the protection area — [`../entraid/protection/threat_assessment.py`](../entraid/protection/threat_assessment.py)

---

## Official docs

- [Microsoft Purview overview](https://learn.microsoft.com/en-us/purview)
- [eDiscovery API](https://learn.microsoft.com/en-us/graph/api/resources/security-ediscoveryoverview)
- [Records management API](https://learn.microsoft.com/en-us/graph/api/resources/security-recordsmanagement-overview)
- [Subject rights request API](https://learn.microsoft.com/en-us/graph/api/resources/security-subjectrightsrequest)
- [Threat assessment API](https://learn.microsoft.com/en-us/graph/api/resources/threatassessment-api-overview)
