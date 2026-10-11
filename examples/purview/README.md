# Microsoft Purview — Compliance & Information Protection

Examples for working with Microsoft Purview compliance, records
management, sensitivity labels, eDiscovery, subject rights, and
threat assessment.

---

## Prerequisites

| Permission | Description | Reference |
|---|---|---|
| `RecordsManagement.ReadWrite.All` | Create and manage retention labels | [Records management permissions](https://learn.microsoft.com/en-us/graph/permissions-reference#records-management-permissions) |
| `InformationProtectionPolicy.Read.All` | Read sensitivity labels | |
| `ThreatAssessment.ReadWrite.All` | Submit URL/file threat assessments | |
| `eDiscovery.ReadWrite.All` | Create eDiscovery cases and searches | |
| `SubjectRightsRequest.ReadWrite.All` | Create and manage subject rights requests | |
| `Sites.ReadWrite.All` | Apply labels to SharePoint files | |

---

## Examples

### Records Management

| Scenario | File | Permission |
|---|---|---|
| Create a retention label | [`records/retention_label.py`](./records/retention_label.py) | `RecordsManagement.ReadWrite.All` |
| List retention labels | [`records/list_retention_labels.py`](./records/list_retention_labels.py) | `RecordsManagement.Read.All` |
| Auto-apply label to unlabeled files (Graph) | [`records/auto_apply_retention_label.py`](./records/auto_apply_retention_label.py) | `RecordsManagement.ReadWrite.All` + `Sites.ReadWrite.All` |
| Auto-apply label via SharePoint CSOM | [`records/auto_apply_label.py`](./records/auto_apply_label.py) | `RecordsManagement.ReadWrite.All` + `Sites.Read.All` |

### Sensitivity Labels

| Scenario | File | Permission |
|---|---|---|
| List sensitivity labels (with priority/description) | [`sensitivity_labels/list.py`](./sensitivity_labels/list.py) | `InformationProtectionPolicy.Read.All` |
| Apply a sensitivity label to a SharePoint file | [`../sharepoint/sites/assign_sensitivity_label.py`](../sharepoint/sites/assign_sensitivity_label.py) | `InformationProtectionPolicy.Read.All` |

### eDiscovery

| Scenario | File | Permission |
|---|---|---|
| eDiscovery full case workflow (case, custodian, search, close) | [`ediscovery/create_and_search.py`](./ediscovery/create_and_search.py) | `eDiscovery.ReadWrite.All` |
| List review sets for a case | [`ediscovery/review_sets.py`](./ediscovery/review_sets.py) | `eDiscovery.ReadWrite.All` |
| Search partially indexed items | [`ediscovery/search_partially_indexed.py`](./ediscovery/search_partially_indexed.py) | `eDiscovery.ReadWrite.All` |

### Subject Rights

| Scenario | File | Permission |
|---|---|---|
| Create a subject rights request | [`subject_rights/create_request.py`](./subject_rights/create_request.py) | `SubjectRightsRequest.ReadWrite.All` |
| List subject rights requests | [`subject_rights/list_requests.py`](./subject_rights/list_requests.py) | `SubjectRightsRequest.Read.All` |

### Threat Assessment

| Scenario | File | Permission |
|---|---|---|
| Submit URL/file threat assessment | [`threat_assessment/scan_url.py`](./threat_assessment/scan_url.py) | `ThreatAssessment.ReadWrite.All` |
| Submit file / email-file threat assessments (protection area) | [`../entraid/protection/threat_assessment.py`](../entraid/protection/threat_assessment.py) | `ThreatAssessment.ReadWrite.All` |

### Security (attack simulation)

| Scenario | File | Permission |
|---|---|---|
| Report phishing-simulation campaigns and training | [`../security/attack_simulation.py`](../security/attack_simulation.py) | `AttackSimulation.Read.All` |

---

## Auth note

- **Records management** and **sensitivity labels** require **delegated
  (interactive)** auth with a Global/Compliance Administrator role — those APIs
  do not support app-only access. The examples use `with_token_interactive`.
- **eDiscovery, subject rights, and threat assessment** work with
  `with_client_secret` (app-only) auth.

## Not yet covered (need library additions)

- eDiscovery **legal holds** (`case.holds`)
- **Retention policies** and **retention events**
- **DLP policies**

---

## Quick start

```python
from office365.graph_client import GraphClient

client = GraphClient(tenant="contoso.onmicrosoft.com").with_client_secret("client_id", "client_secret")

labels = client.security.labels.retention_labels.get().execute_query()
for label in labels:
    print(label.display_name)
```

---

## Official docs

- [Microsoft Purview overview](https://learn.microsoft.com/en-us/purview)
- [Records management API](https://learn.microsoft.com/en-us/graph/api/resources/security-recordsmanagement-overview)
- [eDiscovery API](https://learn.microsoft.com/en-us/graph/api/resources/security-ediscoveryoverview)
- [Subject rights request API](https://learn.microsoft.com/en-us/graph/api/resources/security-subjectrightsrequest)
- [Threat assessment API](https://learn.microsoft.com/en-us/graph/api/resources/threatassessment-api-overview)
