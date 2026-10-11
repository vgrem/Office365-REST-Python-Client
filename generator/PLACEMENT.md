# Placement contract

How the generator decides where a generated type lives. Everything here is
enforced (or asserted) by the tests in `tests/unit/test_generator_placement_contract.py`.

## Target levels

```
office365/                 package root (config `output_path`)
  <level 1>                product (Graph) or service (SharePoint)
    <level 2>              subsystem
      <level 3+>           finer subsystem / metadata namespace
        <type>.py          one type per module
```

- **Level 1 = product**. `microsoft.graph` is a **container namespace**, not a
  product — it unifies OneDrive, Outlook, Teams, Entra, Intune, … The job of
  routing is precisely to **split that container into products** (`directory`,
  `intune`, `communications`, `outlook`, `teams`, `onedrive`, …).
- **Level 1 = service** for SharePoint (`sharepoint`).
- **Level 2 = subsystem** (curated), for services that have them:
  `intune.devices`, `directory.identitygovernance`, `sharepoint.tenant`, …
- **Level 3+** narrows further, often matching the metadata namespace or an
  existing subpackage.
- `office365.runtime` is **infrastructure**, not a product.
- `office365.common` is for **cross-cutting types** — those genuinely used by
  many products (shared value types, vendor-neutral errors, …) and the final
  fallback when no product can be inferred. It must stay small; anything that
  clearly belongs to one product should not land here.

## Decision order (first match wins)

1. **Attached (sticky)** — a file that already defines the type is reused in
   place; an existing type is **never moved**, and its custom members are never
   removed. Metadata additions are appended only.
2. **Exact OData name** — `[type_routing]` entry keyed by the full name.
3. **Namespace** — `[routing]` prefix, e.g.
   `microsoft.graph.security.* → office365.security.*`.
4. **Exact short name** — `[type_routing]` entry keyed by the class name
   (bare `microsoft.graph.*` types only, so it can never shadow a namespace).
5. **Prefix** — `[type_routing]` `Prefix*`, first match in configuration order.
6. **Fallback** — `"*" → office365.common`.

Then **hierarchical descent**: if the routed directory contains a subpackage
whose (underscore-insensitive) name matches the class-name prefix, the file goes
into it with the prefix stripped —
`AccessReviewError → …/accessreview/error.py`, `PrintSettings → …/print/settings.py`.

## Invariants

- **Importable**: every segment of a planned module is a valid Python identifier
  (namespaces like `…Windows.10…` are sanitized to `…windows._10…`).
- **Contained**: every written file is under `output_path` (never outside).
- **Sticky**: attached types resolve to their existing file and are never moved.
- **No gaps**: every in-scope type resolves to a module — the fallback bucket
  guarantees it (nothing is silently unrouted).

## Adding routing (2-stage workflow)

1. `python -m generator.generate_model <service> --suggest-routing` proposes
   `[routing]` / `[type_routing]` entries for unrouted types.
2. Review and paste them into `generator/settings.<service>.yaml`.
3. `python -m generator.generate_model <service> --force` generates.

The tool proposes; a human commits. **Routing is never written automatically.**
