# Sensitivity labels

Sensitivity labels classify content by confidentiality — Public, Internal,
Confidential, Highly Confidential — and the classification travels with the
content. The Graph entry point is
`client.security.data_security_and_governance.sensitivity_labels`.

## [List sensitivity labels](list.py)

Lists the labels published in the tenant, with priority and description on
demand.

```python
labels = client.security.data_security_and_governance.sensitivity_labels.get().execute_query()
for label in labels:
    print(label.display_name, label.priority)
```

```bash
python list.py
python list.py --detail
```

Requires the **delegated** permission `InformationProtectionPolicy.Read.All`
**and** the Compliance Administrator (or Global Administrator) role — the script
uses `with_token_interactive` with a `require_role` pre-flight guard.

## See also

- Apply a sensitivity label to a SharePoint file — [`../../sharepoint/sites/assign_sensitivity_label.py`](../../sharepoint/sites/assign_sensitivity_label.py)

## Official docs

- [List sensitivity labels](https://learn.microsoft.com/en-us/graph/api/informationprotectionpolicy-list-labels)
- [Sensitivity labels overview](https://learn.microsoft.com/en-us/purview/sensitivity-labels)
