"""Detect reference cycles among generated types.

Each type is written to its own module, so a reference cycle between types is
also a module import cycle. The generator breaks such cycles by defaulting the
offending dataclass fields to ``None`` (annotation-only import) instead of
constructing the referenced type eagerly.
"""

from __future__ import annotations


def find_cyclic_types(model, in_scope: set[str]) -> set[str]:
    """Types that participate in a reference cycle (strongly connected component).

    Only references inside ``in_scope`` count; a component of size > 1 is a real
    mutual dependency (a self-reference stays within one module and is fine).
    """
    edges: dict[str, set[str]] = {}
    for name in in_scope:
        schema = model.types.get(name)
        if schema is None:
            continue
        targets: set[str] = set()
        for prop in schema.Properties.values():
            if not prop.TypeName:
                continue
            item = prop.type_ref.text
            if item in in_scope and item != name:
                targets.add(item)
        edges[name] = targets

    index = 0
    indices: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    cyclic: set[str] = set()

    def strong_connect(node: str) -> None:
        nonlocal index
        indices[node] = low[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for neighbor in edges.get(node, ()):
            if neighbor not in indices:
                strong_connect(neighbor)
                low[node] = min(low[node], low[neighbor])
            elif neighbor in on_stack:
                low[node] = min(low[node], indices[neighbor])
        if low[node] == indices[node]:
            component = []
            while True:
                member = stack.pop()
                on_stack.discard(member)
                component.append(member)
                if member == node:
                    break
            if len(component) > 1:
                cyclic.update(component)

    for name in edges:
        if name not in indices:
            strong_connect(name)
    return cyclic
